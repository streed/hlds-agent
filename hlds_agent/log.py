import logging

log = None

if not log:
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)

    log = logging.getLogger('hlds-agent')
    log.setLevel(logging.DEBUG)
    log.addHandler(ch)
