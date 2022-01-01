import argparse
from datetime import datetime, timedelta


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

    # Create an empty list to put the resulting entries in
    parsed_gift_entries = []

    # Iterate through the entries
    for raw_gift_entry in raw_gift_entries:
        
        # Parse the entry
        parsed_gift_entries.append(_parse_gift_entry(raw_gift_entry))
    
    # Return the resulting list of parsed gift entries
    return parsed_gift_entries
        

def _parse_gift_entry(raw_gift_entry):
    '''
    Helper function that parses a single
    gift entry.
    '''

    # Example gift entry:
    # 'Dec 30 2021, 10:52 pm - Standalone Ship - Origin G12 - Warbond #69696969 - Gifted to recipient@mail.com, value: $420.00 USD'

    # Split entry string by ' - '
    raw_gift_entry_split = raw_gift_entry.split(' - ')

    # Extract the date and time (first item in the list)
    date_time_string = raw_gift_entry_split.pop(0)
    
    # Convert the am/pm at the end to AM/PM to follow us_en locale
    # Example: 'Dec 30 2021, 10:52 pm' -> 'Dec 30 2021, 10:52 PM'
    date_time_string = date_time_string[:-2] + date_time_string[-2:].upper()

    # Parse the date time string. Example: 'Dec 30 2021, 10:52 PM'
    datetime_object = datetime.strptime(date_time_string, '%b %d %Y, %I:%M %p')

    # The last item in raw_gift_entry_split is the recipient and value.
    # Example: 'Gifted to recipient@mail.com, value: $420.00 USD'
    recipient_and_value = raw_gift_entry_split.pop(-1)

    # Extract recipient
    recipient = recipient_and_value.split(', ')[0].split(' ')[-1]

    # Extract value
    value = float(recipient_and_value.split(', ')[-1].split('$')[-1].split(' ')[0])

    # Build the parsed entry dict
    parsed_gift_entry = {
        'time': datetime_object,
        'recipient': recipient,
        'value': value
    }

    # Return the parsed entry dict
    return parsed_gift_entry


def build_calendar(parsed_gift_entries):
    '''
    Ingests a list of parsed gift entries,
    finds the earliest date in gift entries
    (to be called the start date) and latest
    date in gift entries + 24 hours (to be called
    the end date). Using these dates, it creates
    a calendar of every minute between the start
    and end dates, then populates each minute
    with the total value of ships/items gifted in
    the 24 hours leading up to that minute.
    '''

    # Find start date
    start_date = find_earliest_date(parsed_gift_entries)

    # Find end date
    end_date = find_latest_date(parsed_gift_entries) + timedelta(days=1)

    # Calculate number of minutes between start and end date
    calendar_length = int((end_date - start_date).total_seconds()/60)

    # Build a blank calendar with that number of entries
    calendar = [0 for i in range(calendar_length)]

    # Add entries to the calendar
    for entry in parsed_gift_entries:
        calendar = add_entry_to_calendar(entry, calendar, start_date)

    # Return the populated calendar
    return calendar, start_date
  

def find_earliest_date(parsed_gift_entries):
    '''
    Given a list of parsed gift entries,
    this function finds the earliest date
    among them.
    '''

    # Create a basic max date object to start comparisons
    earliest_date = datetime.max

    # Iterate through gift entries
    for entry in parsed_gift_entries:
        if entry['time'] < earliest_date:
            earliest_date = entry['time']
    
    # Return the earliest date
    return earliest_date


def find_latest_date(parsed_gift_entries):
    '''
    Given a list of parsed gift entries,
    this function finds the latest date
    among them.
    '''

    # Create a basic max date object to start comparisons
    latest_date = datetime.min

    # Iterate through gift entries
    for entry in parsed_gift_entries:
        if entry['time'] > latest_date:
            latest_date = entry['time']
    
    # Return the latest date
    return latest_date


def add_entry_to_calendar(entry, calendar, start_date):
    '''
    Adds a single entry to the calendar
    '''

    # Store the number of minutes in a day
    mins_in_day = 1440

    # Figure out when this entry is inserted into the calendar 
    insert_point = int((entry['time'] - start_date).total_seconds()/60)

    # For each item in the calendar between the time on the entry
    # and 24 hours after the time on the entry, add the value of the
    # entry to that item.

    # Set the starting point of the counter to where this entry is inserted
    counter = insert_point

    # Iterate through the 24 hour period that this gift entry affects
    for item in calendar[insert_point:insert_point + mins_in_day]:
        
        # Add the value of the entry to the calendar for that minute
        calendar[counter] += entry['value']

        # Increase counter to iterate
        counter += 1
    
    # Return the calendar with the single entry added
    return calendar


def find_earliest_sell_date(calendar, start_date, desired_sell_price):
    '''
    Iterates through all entries in the calendar
    after the current time to find the next
    possible time that you will be eligible to sell
    a ship of the specified input price.
    '''

    # Store the max amount of money that can be gifted in 24h
    max_gift_value_per_day = 1000

    # Find where the current time is on the calendar object
    starting_point = int((datetime.utcnow() - start_date).total_seconds()/60)

    # Iterate through every minute after the current minute
    counter = starting_point
    for minute in calendar[starting_point:]:

        # If the current minute plus the desired sell price is less than
        # CIG's max sell amount per day, you should be able to sell. 
        # Therefore, this is the time we want to choose
        if minute + desired_sell_price < max_gift_value_per_day:
            break

        # If not, move onto the next minute
        counter += 1
    
    # Once the right minute is found, convert it into a date
    earliest_sell_date = start_date + timedelta(minutes=counter)

    # Return the earliest sell date
    return earliest_sell_date 


def save_calendar_to_file(calendar, start_date, output_file_name):
    '''
    Output a human-readable calendar
    '''

    # Open output file
    with open(output_file_name, 'w') as outfile:

        # Iterate through each minute in the calendar
        counter = 0
        for minute in calendar:

            # Build human readable datetime for this minute
            curr_datetime = start_date + timedelta(minutes=counter)

            # Build output string for single line
            out_string = f"{curr_datetime} -> ${minute:.2f} spent in last 24h.\n"

            # Write output string to file
            outfile.write(out_string)

            # Iterate
            counter += 1


def announce_results(earliest_sell_date, desired_sell_price):
    '''
    Announces the results to the console for the user
    '''

    print(f"The next time you will be able to gift a ship valued at ${desired_sell_price:.2f} will be at {earliest_sell_date} UTC (make sure to convert to your timezone)")


def main():

    # Ingest input arguments
    input_file_name, output_file_name, desired_sell_price = ingest_args()

    # Read in the contents of the log file
    log_entries = read_hangar_log(input_file_name)
    
    # Extract entries related to giving gifts
    raw_gift_entries = filter_gift_entries(log_entries)
    
    # Parse the gift entries into dictionaries
    parsed_gift_entries = parse_gift_entries(raw_gift_entries)
    
    # Build calendar
    calendar, start_date = build_calendar(parsed_gift_entries)
    
    # Find the earliest possible date that a ship of specified value could be sold
    earliest_sell_date = find_earliest_sell_date(calendar, start_date, desired_sell_price)
    
    # Print human-readable output
    announce_results(earliest_sell_date, desired_sell_price)
    
    # Save the calendar to a file
    if output_file_name is not None:
        save_calendar_to_file(calendar, start_date, output_file_name)


if __name__ == '__main__':
    main()