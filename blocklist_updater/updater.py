import argparse
import logging
import signal
import asyncio
import sys
import os
import blocklist_aggregator

from dotenv import load_dotenv

logger = logging.getLogger("updater")
loop = asyncio.get_event_loop()
shutdown_task = None

def setup_logger(debug):
    loglevel = logging.DEBUG if debug else logging.INFO
    logfmt = '%(asctime)s %(levelname)s %(message)s'
    
    logger.setLevel(loglevel)
    logger.propagate = False
    
    lh = logging.StreamHandler(stream=sys.stdout )
    lh.setLevel(loglevel)
    lh.setFormatter(logging.Formatter(logfmt))    
    
    logger.addHandler(lh)

async def updater(every, start_shutdown, blocklist_config, blocklist_format, blocklist_output):
    while not start_shutdown.is_set():
        logger.debug("generating blocklist...")
        try:
            if blocklist_format == "cdb":
                blocklist_aggregator.save_cdb(filename=blocklist_output, cfg_filename=blocklist_config)
            elif blocklist_format == "hosts":
                blocklist_aggregator.save_hosts(filename=blocklist_output, cfg_filename=blocklist_config)
            elif blocklist_format == "raw":
                blocklist_aggregator.save_raw(filename=blocklist_output, cfg_filename=blocklist_config)
            else:
                logger.error("invalid blocklist format %s" % blocklist_format)
        except Exception as e:
            logger.error("blocklist_aggregator: %s" % e)
        
        logger.debug("re-generate in %s seconds" % every)
        try:
            await asyncio.wait_for(start_shutdown.wait(), timeout=every)
        except asyncio.TimeoutError:
            pass

async def shutdown(signal, loop, start_shutdown):
    """perform graceful shutdown"""
    logger.debug("starting shutting down process")
    start_shutdown.set()

    current_task = asyncio.current_task()
    tasks = [
        task for task in asyncio.all_tasks()
        if task is not current_task
    ]

    logger.debug("waiting for all tasks to exit")
    await asyncio.gather(*tasks, return_exceptions=True)

    logger.debug("all tasks have exited, stopping event loop")
    loop.stop()

def start_updater():
    # default values
    debug = False
    delay_every = 3600

    # read config from environnement file ?
    options = argparse.ArgumentParser()
    options.add_argument("-e", help="env config file") 

    args = options.parse_args()
    if args.e != None:
        load_dotenv(dotenv_path=args.e)

    # read environment variables
    debug_env = os.getenv('BLOCKLIST_UPDATER_DEBUG')
    if debug_env is not None:
        debug = bool( int(debug_env) )

    # enable logger
    setup_logger(debug=debug)

    delay_env = os.getenv('BLOCKLIST_UPDATER_EVERY')
    if delay_env is not None:
        delay_every = int(delay_env)

    blocklist_config = os.getenv('BLOCKLIST_UPDATER_CONFIG_PATH')
    if blocklist_config is None:
        logger.error("missing env variable BLOCKLIST_UPDATER_CONFIG_PATH")
        sys.exit(1)

    blocklist_format = os.getenv('BLOCKLIST_UPDATER_OUTPUT_FORMAT')
    if blocklist_format is None:
        logger.error("missing env variable BLOCKLIST_UPDATER_OUTPUT_FORMAT")
        sys.exit(1)
    if blocklist_format not in ["cdb", "hosts", "raw"]:
        logger.error("invalid blocklist format provided")
        sys.exit(1)

    blocklist_output = os.getenv('BLOCKLIST_UPDATER_OUTPUT_PATH')
    if blocklist_output is None:
        logger.error("missing env variable BLOCKLIST_UPDATER_OUTPUT_PATH")
        sys.exit(1)

    # prepare shutdown handling
    start_shutdown = asyncio.Event()
    for sig in (signal.SIGHUP, signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(
            shutdown(sig, loop, start_shutdown)
        ))

    # run monitor
    loop.create_task(
                    updater(
                            every=delay_every,
                            start_shutdown=start_shutdown,
                            blocklist_config=blocklist_config,
                            blocklist_format=blocklist_format,
                            blocklist_output=blocklist_output,
                        )
                    )
    
    # run event loop 
    try:
       loop.run_forever()
    finally:
       loop.close()
    
    logger.debug("app terminated")