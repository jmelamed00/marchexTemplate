from datetime import datetime
import argparse



def processArguments():
    arguments = {}
    parser = argparse.ArgumentParser(description='Supply Inputs: --token')
    parser.add_argument('--token', nargs=1)

    args = parser.parse_args()
    arguments['token'] = args.token[0]

    return arguments
