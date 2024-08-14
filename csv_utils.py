import csv
import datetime as dt
from typing import List, Tuple

def read_csv(filename: str) -> Tuple[List[dt.date], List[dt.timedelta]]:
    """Read in the CSV file with the provided name 
    and return lists of the dates and durations.
    """
    try:
        with open(filename, mode='r', newline='') as csv_data:
            csv_reader = csv.reader(csv_data)
            fields = next(csv_reader)
            # print('Fields:', fields)
            dates = []
            durations = []
            for row in csv_reader:
                dates.append(dt.date.fromisoformat(row[0]))
                h, m = map(int, row[1].split(':'))
                durations.append(dt.timedelta(hours=h, minutes=m))
        return dates, durations
    except FileNotFoundError:
        print('Error: file not found')
        return ([],[])

def write_csv(
        filename: str, dates: List[dt.date], 
        durations: List[dt.timedelta]) -> None:
    """Format the provided dates and durations and write them to a new
    CSV file with the given name.
    (Checking that the filename doesn't already exist to avoid 
    overwriting should be performed in a different function.)
    """
    data = [['date', 'duration']]
    for date, duration in zip(dates, durations):
        date_str = date.strftime('%Y-%m-%d')
        total_minutes = int(duration.total_seconds() / 60)
        hours, minutes = divmod(total_minutes, 60)
        duration_str = f'{hours:02}:{minutes:02}'
        data.append([date_str, duration_str])
    
    with open(filename, mode='w', newline='') as new_csv:
        writer = csv.writer(new_csv)
        writer.writerows(data)

def append_csv(
        filename: str, dates: List[dt.date], 
        durations: List[dt.timedelta]) -> None:
    """Format the provided dates and durations and append them to the 
    CSV file with the given name.
    """
    try:
        with open(filename, mode='a', newline='') as existing_csv:
            csv_writer = csv.writer(existing_csv)
            data = []
            for date, duration in zip(dates, durations):
                date_str = date.strftime('%Y-%m-%d')
                total_minutes = int(duration.total_seconds() / 60)
                hours, minutes = divmod(total_minutes, 60)
                duration_str = f'{hours:02}:{minutes:02}'
                data.append([date_str, duration_str])
            csv_writer.writerows(data)
    except FileNotFoundError:
        print('Error: file not found')
