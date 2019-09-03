# load packages, if not installt uncomend:
# install.packages("httr")
# install.packages("jsonlite")

# This is a short example of using R with IoTree42 rest api.

require("httr")
require("jsonlite")

start_time <- Sys.time()

# Get token, insert in your credentials.
url_token <- '< your url to/ ip:port >/api-token-auth/?format=json'
url <- '< your url / ip:port >/iotree_api/?format=json'
query <- list(
  username = jsonlite::unbox('<username>'), # Enter your username here.
  password = jsonlite::unbox('<password>') # Enter your password here.
)
column_name_1 <- # Column of the Unix time. Unix column is always available when the server detects the time column.
column_name_2 <- "Time" # column of time
column_name_3 <- "pm_25" # column of particulate matter pm 2.5
column_name_4 <- "pm_10" # column of particulate matter pm 10


results_token <- POST(url_token, body = query,  encode = "json")
raw_token <- content(results_token)
prefix <-"Token"
token <- paste(prefix, raw_token, sep = " ")

# Get all available gateways.
gateways <- GET(url, add_headers(Authorization = token))
print(gateways)
# Make a request for your data and send it to the API.
gateway_id <- content(gateways)[[1]][[2]] # Choose one of the available gateways.

query <- list(
  gateway_id = jsonlite::unbox(gateway_id), # Insert the gateway_id
  tree = jsonlite::unbox([]), # insert the tree branch, example: ["gatewayself", "sensor"]
  filters = jsonlite::unbox('data'), # insert ether 'data' or 'tree'
  in_order = jsonlite::unbox('True'), # insert bool if tree (branch) should be queried in order or not.
  negated = jsonlite::unbox('False'), # insert bool if tree (branch) should be queried as negative or not.
  #time_start = jsonlite::unbox(1562793111000), # insert start time in UNIX-Time in milisec
  time_start = jsonlite::unbox(0.0), # insert start time in UNIX-Time 
  time_end = jsonlite::unbox('now') # insert end time in UNIX-Time. You can use "now" for current time.
  )
results <- POST(url, add_headers(Authorization = token), body = query,  encode = "json")
json_string <- content(results)

# read content in list for later use.
posts_body <- json_string[[1]]["posts_body"][[1]] # all the data
posts_head <- json_string[[1]]["posts_head"][[1]] # all the column names
posts_tree <- json_string[[1]]["posts_tree"][[1]] # the tree branch

# get column index of desired values.
tree <- toString(posts_tree, width = NULL)
index_unix <- match(column_name_1, posts_head)
index_time <- match(column_name_2, posts_head)
index_pm_25 <- match(column_name_3, posts_head)
index_pm_10 <- match(column_name_4, posts_head)

# loop to post_body list to get all values for each column. 
xtime_time <- numeric(length = 0)
for (n in posts_body) {
  xtime_time <- append(xtime_time, n[[index_time]])
}
xtime_unix <- numeric(length = 0)
for (n in posts_body) {
  xtime_unix <- append(xtime_unix, n[[index_unix]])
}
y25 <- numeric(length = 0)
for (n in posts_body) {
  y25 <- append(y25, n[[index_pm_25]])
}
y10 <- numeric(length = 0)
for (n in posts_body) {
  y10 <- append(y10, n[[index_pm_10]])
}

# plot all data
xy <- data.frame(xtime_unix,y25) # choose your desired column.
subtitel <- paste("Gateway:", gateway_id, sep = " ")
titel <- paste("tree branch:", tree, sep = " ")
plot(xy, xlab = posts_head[[index_unix]], ylab = posts_head[[index_pm_25]], sub=subtitel, main=titel)

end_time <- Sys.time()
print(end_time - start_time) # Stopwatch to execute all.
