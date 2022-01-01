import argparse
from datetime import datetime


def ingest_args():
    '''
    Ingests the input arguments for the program
    '''

    # Create the parser and add a basic description of what this program does
    parser = argparse.ArgumentParser(description='Generates a calendar for your Star Citizen gifts and determines the next time you can send a ship of a given value without hitting CIG\'s gift sending limit.')
    
    # Add individual arguments
    parser.add_argument('-i', '--input-file', dest='inputfilename', required=True, type=str, help='Location of the file containing SC hangar logs.')
    parser.add_argument('-o', '--output-file', dest='outputfilename', required=False, type=str, help='This program generates a calendar that is represented by an array of floats. Each item in the array represents 1 minute, starting from the earliest date of a gift found in the hangar logs and ending 24 hours after the latest date of a gift found in the hangar logs. The value stored in each index of the array represents the total dollars gifted in the 24 hours prior to that minute. This can be helpful to show the sliding scale of how your gifting restrictions drop off. Not required to determine the date of your next sale, only populate this flag if you want the raw calendar data.')
    parser.add_argument('-p', '--price', dest='desiredsellprice', required=True, type=float, help='The price of the ship you want to gift.')

    # Parse the arguments
    args = parser.parse_args()

    # Collect the argument
    input_file_name = args.inputfilename
    output_file_name = args.outputfilename
    desired_sell_price = args.desiredsellprice

    # Return the values
    return input_file_name, output_file_name, desired_sell_price


def read_hangar_log(input_file_name):
    '''
    Opens the hangar log file and reads 
    in the contents, stripping out any 
    extra lines.
    '''

    # Open the file
    with open(input_file_name, 'r') as input_file:

        # Extract the raw data from the log file
        raw_log_lines = input_file.readlines()
    
    # Strip unnecessary characters and lines
    log_lines = [line.strip() for line in raw_log_lines if line != '\n']
    
    # Return the raw log line data
    return log_lines


def filter_gift_entries(log_entries):
    '''
    Ingests a list of log entries and
    only returns the entries that pertain
    to sending gifts
    '''

    # Find entries that contain "Gifted to"
    gift_entries = [entry for entry in log_entries if "Gifted to" in entry]

    # Return the gift entries
    return gift_entries


def parse_gift_entries(raw_gift_entries):
    '''
    Ingests a list of strings, each containing
    an entry pertaining to giving a gift.
    For each gift entry, this function splits
    the string into its relevant data pieces
    and stores each as a dict.
    Returns a list of dicts, one per gift entry.
    '''

    # Example gift entry:
    # 'Dec 30 2021, 10:52 pm - Standalone Ship - Origin G12 - Warbond #69696969 - Gifted to recipient@mail.com, value: $420.00 USD'

    # Extract the date and time
    d

def main():

    # Ingest input arguments
    input_file_name, output_file_name, desired_sell_price = ingest_args()

    # Read in the contents of the log file
    log_entries = read_hangar_log(input_file_name)
    
    # Extract entries related to giving gifts
    raw_gift_entries = filter_gift_entries(log_entries)
    
    # Parse the gift entries into dictionaries
    parsed_gift_entries = parse_gift_entries(raw_gift_entries)


if __name__ == '__main__':
    main()