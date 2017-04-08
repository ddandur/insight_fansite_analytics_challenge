"""// your Python code to implement the features could be placed here
// note that you may use any language, there is no preference towards Python
"""

from sys import argv
from collections import Counter, deque
import datetime
import heapq

########################################
# Define BusyCounter class
########################################

class BusyCounter(object):
    # keeps track of current 60-minute window and the top-n most busy windows
    # this assumes data is entered in chronological order as shown in examples

    def __init__(self, start_t, top_n=10, window_width=3600):
        self.top_n = top_n # number of busiest 60-minute periods to count
        self.ts_deque = deque() # stores all time stamps in current 60-minute period
        self.top_times_heap = [] # heap of top_n 60-minute period time_stamps and their counts
        self.start_t = start_t   # start datetime object of current 1-hour interval
        self.end_t = start_t + datetime.timedelta(0, window_width-1) # end of current time period (inclusive), so this time
                                                           # is considered part of current period
        self._one_second = datetime.timedelta(0, 1)

    def insert(self, new_time_stamp):
        """insert new time-stamp (datetime object) into object"""

        # if new_time_stamp in current one-hour window, simply add to internal deque
        if new_time_stamp <= self.end_t:
            self.ts_deque.append(new_time_stamp)
        # otherwise, increment boundaries of deque one second at a time and record website hits
        # for each boundary set until new self.end_t equals new_time_stamp
        else:
            while self.end_t < new_time_stamp:
                # if heap not full yet, simply add start time with counts
                if len(self.top_times_heap) < self.top_n:
                    heapq.heappush(self.top_times_heap, (len(self.ts_deque), self.start_t))
                # else if current time period has more hits than min of self.top_times_heap,
                # pop old value and add new one (otherwise current window and counts are discarded)
                elif len(self.ts_deque) > self.top_times_heap[0][0]:
                    heapq.heappop(self.top_times_heap)
                    heapq.heappush(self.top_times_heap, (len(self.ts_deque), self.start_t))
                # increment window by one second
                self.start_t = self.start_t + self._one_second
                self.end_t = self.end_t + self._one_second
                # leftpop off all time_stamps that are less than current start time from self.ts_deque
                while self.ts_deque and self.ts_deque[0] < self.start_t:
                    self.ts_deque.popleft()

    def add_last_windows(self):
        """once file done reading, add last windows (if applicable) to
        self.top_times_heap"""
        while len(self.ts_deque) > 0:

            # if heap not full yet, simply add start time with counts
            if len(self.top_times_heap) < self.top_n:
                heapq.heappush(self.top_times_heap, (len(self.ts_deque), self.start_t))
            # else if current time period has more hits than min of self.top_times_heap,
            # pop old value and add new one (otherwise current window and counts are discarded)
            elif len(self.ts_deque) > self.top_times_heap[0][0]:
                heapq.heappop(self.top_times_heap)
                heapq.heappush(self.top_times_heap, (len(self.ts_deque), self.start_t))
            # move beginning of window forward one second
            self.start_t = self.start_t + self._one_second
            # leftpop off all time_stamps that are less than current start time from self.ts_deque
            while self.ts_deque and self.ts_deque[0] < self.start_t:
                self.ts_deque.popleft()

########################################
# Define BlockCounter class
########################################

class BlockCounter(object):
    """Keeps track of which login attempts are recorded to blocked file

    failed_dict: stores data in form {address: [start_time, count]}, where
                 start_time is beginning of 20-second timer and count is how
                 many failed logins there have been in current 20-second timer
    blocked_dict: stores data in form {address: start_time}, where start_time
                  is beginning of current 5-minute blocked period

    Rather than clearing out failed_dict and blocked_dict at each time step,
    we allow them to record old information that only gets updated if a new
    request from the same IP address comes in. This tradeoff uses more
    memory, but it saves time by not requiring a time-consuming search through
    the dicts for old values to drop at every step.
    """

    def __init__(self):
        self.failed_dict = {} # records failed logins on 20 second timer
        self.blocked_dict = {} # records which addresses are currently blocked
        self._twenty_seconds = datetime.timedelta(0, 20)
        self._five_minutes = datetime.timedelta(0, 5*60)

    def insert(self, line_data):
        """ Insert new entry into BlockCounter object.
        Insertion first checks whether requesting address is blocked, and if so
        records it into blocked.txt.
        If request is failed, it then checks whether this address is in current
        20-second timer (i.e., in failed_dict). If not, it is added, and if so,
        count in 20-second timer (failed_dict) is incremented. If incremented
        count is 3, the address is deleted from 20-second timer and added to
        the 5-minute blocked dict.
        """

        # check whether requesting address is currently blocked and if so
        # print log entry to blocked.txt
        if line_data["host"] in self.blocked_dict:
            self._update_blocked(line_data)

        # if login is failed, update failed_dict (and potentially blocked_dict)
        # as necessary
        if line_data["host"] not in self.blocked_dict and line_data["http_reply_code"] == "401":
            self._update_failed(line_data)

    def _update_blocked(self, line_data):
        # update blocked_dict entry for line_data and record data if necessary
        if self.blocked_dict[line_data["host"]] + self._five_minutes >= line_data["time_stamp"]:
            # print entry to blocked.txt (Task 4)
            with open(argv[5], "a") as f:
                f.write(line_data["original_line"] + "\n")
        else:
            # remove entry from blocked list
            del self.blocked_dict[line_data["host"]]

    def _update_failed(self, line_data):
        # update failed entry for line_data and record to blocked_dict if necessary

        # if item not in failed_dict, add it
        if line_data["host"] not in self.failed_dict:
            self.failed_dict[line_data["host"]] = [line_data["time_stamp"], 1]
        # if in dictionary, determine whether timer needs reset
        else:
            # if outside 20-second timer range, reset timer and counter
            if self.failed_dict[line_data["host"]][0] + self._twenty_seconds < line_data["time_stamp"]:
                self.failed_dict[line_data["host"]] = [line_data["time_stamp"], 1]
            # if inside 20-second timer, increment counter
            else:
                self.failed_dict[line_data["host"]][1] += 1
                # if counter has hit 3, remove from failed_dict and
                # add to blocked_dict
                if self.failed_dict[line_data["host"]][1] == 3:
                    del self.failed_dict[line_data["host"]]
                    self.blocked_dict[line_data["host"]] = line_data["time_stamp"]

########################################
# Extract information from line in file
########################################

def extract_line_data(line):
    """ input: line (str): line read from input log file
    output (dict): dictionary of values extracted from line
    """

    line = line.strip()
    line_split = line.split()
    # extract values of interest
    host = line_split[0]
    time_stamp = line_split[3] + " " + line_split[4]

    # pop from end to keep operates at O(length of string)
    bytes_number = line_split.pop()
    http_reply_code = line_split.pop()

    # now join everything from index 6 until end of string as request
    request = " ".join(x for x in line_split[5:])

    # convert string numbers to ints
    if bytes_number == "-":
        bytes_number = "0"
    bytes_number = int(bytes_number)

    # turn timestamp into datetime object (ignoring time zone)
    time_stamp = time_stamp[1:-7]
    time_stamp = datetime.datetime.strptime(time_stamp, '%d/%b/%Y:%H:%M:%S')

    return {"host": host, "time_stamp": time_stamp, "request": request,
            "http_reply_code": http_reply_code, "bytes": bytes_number,
            "original_line": line}

def get_resource(request_string):
    """ input (str): request_string of resources
    output (str): string of resource alone

    e.g., for request string '"GET /history/apollo/ HTTP/1.0"', output is
    '/history/apollo/'
    """
    request_string = request_string.split()
    return request_string[1]

########################################
# Error handling for input
########################################

def argument_error():
    """ Display error message if wrong number of arguments used
    """
    print
    print "Error! Wrong number of arguments."
    print "Need name of source file, input file and four names of output files."
    print
    print "Example:"
    print
    print "python ./src/process_log.py ./log_input/log.txt" \
          "./log_output/hosts.txt ./log_output/hours.txt" \
           "./log_output/resources.txt ./log_output/blocked.txt"
    print

########################################
# Main
########################################

def main():
    """ argv should contain, in order:
    ./src/process_log.py (source file)
    ./log_input/log.txt (input data path)
    ./log_output/hosts.txt
    ./log_output/hours.txt
    ./log_output/resources.txt
    ./log_output/blocked.txt
    """
    if len(argv) != 6:
        argument_error()
        return None

    # create hosts counter
    hosts_counter = Counter()
    # create bandwidth counter
    bandwidth_counter = Counter()
    # instantiate busiest-period object with first date
    with open(argv[1], 'r') as f:
        first_line_data = extract_line_data(f.readline())
    busy_counter = BusyCounter(first_line_data["time_stamp"])
    # instantiate block_counter object
    block_counter = BlockCounter()

    #########################
    # Collect information
    #########################

    # iterate through log file, one line at a time
    with open(argv[1], 'r') as f:
        for line in f:
            # extract data from line
            line_data = extract_line_data(line)
            # add host count
            hosts_counter[line_data["host"]] += 1
            # add bandwidth count
            bandwidth_counter[get_resource(line_data["request"])] += \
                                                    line_data["bytes"]
            # add time_stamp to busy_counter object
            busy_counter.insert(line_data["time_stamp"])
            # add line_data to block_counter object
            block_counter.insert(line_data)

    # add last window count to busy_counter object
    busy_counter.add_last_windows()

    #############################################################
    # Create output files (blocked file for Task 4 already done)
    #############################################################

    # print host info to output file (Task 1)
    with open(argv[2], "a") as f:
        for host_count in hosts_counter.most_common(10):
            f.write(host_count[0] + "," + str(host_count[1]) + "\n")

    # print bandwidth information (Task 2)
    with open(argv[4], "a") as f:
        for band_count in bandwidth_counter.most_common(10):
            f.write(band_count[0] + "\n")

    # print top 10 most busy 60-minute windows information (Task 3)
    busy_times = [heapq.heappop(busy_counter.top_times_heap)
                            for _ in range(len(busy_counter.top_times_heap))]
    sorted_busy_times = sorted(busy_times, key = lambda tup: (-tup[0], tup[1]))
    with open(argv[3], "a") as f:
        for i in range(len(sorted_busy_times)):
            time_tuple = sorted_busy_times[i]
            time_str = time_tuple[1].strftime('%d/%b/%Y:%H:%M:%S -0400')
            time_counts = time_tuple[0]
            f.write(time_str + "," + str(time_counts) + "\n")





"""
    with open(argv[3], "a") as f:
        for i in range(len(busy_times)):
            time_tuple = busy_times[-(i+1)]
            time_str = time_tuple[1].strftime('%d/%b/%Y:%H:%M:%S -0400')
            time_counts = time_tuple[0]
            f.write(time_str + "," + str(time_counts) + "\n")
            """





if __name__ == '__main__':
    main()
