'Command-line script to process SMS messages'
import script_process
from georegistry.libraries import sms


def run(settings):
    'Connect to IMAP server and process messages'
    countByKey = sms.process(settings)
    return '\n'.join('%s: %s' % (key, count) for key, count in countByKey.iteritems())


# If we are running standalone,
if __name__ == '__main__':
    # Parse
    argumentParser = script_process.ArgumentParser(
        description='Process SMS messages in mailbox')
    args = argumentParser.parse_args()
    # Run
    message = run(script_process.initialize(args))
    # Say
    if args.verbose:
        print message
