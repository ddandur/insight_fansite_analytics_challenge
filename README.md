# Summary of `process_log.py`

I put all my code into a single python file. My thinking for each part of problem is described here. 

## General Approach

In general, this challenge emphasized speed. My inclination was therefore to use memory freely to get faster performance. My main goal was to accomplish all four tasks with a single pass through all the data. This approach would allow the code to be modified and applied in a streaming fasion on actual data in real-time, with the blocking-file being generated on-the-fly perhaps a report every so often on busiest time periods, etc. 

The BusyCounter and BlockCounter classes that I use for Tasks 3 and 4 are based on assumption that data will be read in sequentially, one line at a time, with only a single pass. 

The `main()` function in `process_log.py` essentially initializes the counting objects, reads through dataset once line-by-line, and prints outputs to their appropriate files.

## Tasks 1 and 2

Theses tasks are about counting up things in the dataset. A hash table (python dictionary) is a fast solution for this. For example, for finding most active IP addresses, each new IP address is either added to hash table and given count 1, or if it already exists in dictionary, has its counter incremented by 1. Task 2 with most active resources operates similarly, where we count bytes instead of website hits. 

I used the python class `Counter` for counting, but the implementation of Counter is simply the hash table idea above. Using `Counter` makes the code a little easier to read. 

At the end of the task the counter objects could be quite large. If the top-10 information is all that is desired, a real application should record this information and then clear the memory from the counter objects. 

## Task 3: Busiest 60-minute periods

For this task I wrote a class `BusyCounter` that handles the incrementing of 60-minute time periods and recording of busiest time periods so far. This class allows the user to change the time-window and how many windows are desired for recording. 

As `main()` reads through data line-by-by, `BusyCounter` keeps track of the current 60-minute time interval and adds the current data point into that interval if appropriate. The data points in the current 60-minute interval are stored in a python deque (essentially a doubly-linked list), which allows for fast (O(1) constant time) appending and popping to both ends of the deque.

Once a data point is reached that falls outside the current interval, `BusyCounter` records the number of website hits from the last 60-minute interval and advances the current 60-minute interval by one second. In addition, if the recorded number of website hits from the previous 60-minute interval is in the current top-10, that value is added to the `top_times_heap` attribute. 

The top times are stored as a heap in `top_times_heap` to make for fast insertions. Checking the smallest value (smallest number of hits in 60-minute period) in heap takes constant time, and insertion takes log(n) time in length n of heap. This is faster than the n-time insertion into a regular python list and would begin to matter for longer lists or more frequent insertion operations.

## Task 4: Failed Logins

For this task I wrote a class `BlockCounter` that keeps track of currently-blocked addresses and addresses that have had recent failed logins in the dictionaries `failed_dict` and `blocked_dict`. In order to make code run as fast as possible, I do not update either dictionary unless I encounter that IP address again; this means these dictionaries will carry around "expired" data, but it saves the times of having to go through both dictionaries to update them at each line of read data. In this case I again decided to use more memory in order to save time.


## Helper Functions

`extract_line_data` and `get_resource` are used to extract data from log file. These functions are brittle to corrupted data, and if I had more time I would implement more checking at this step. I would also implement a function that would save corrupted data lines to a separate output file if they are not used in data recording.

I also use `argument_error` as a small check in case the wrong number of arguments are used on command line.

## Testing 

I wrote code using an Ipython notebook, which is where I did most testing. If I had more time I would add those tests as a testing suite inside this repo. 


