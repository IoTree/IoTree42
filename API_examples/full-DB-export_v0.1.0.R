# load packages, if not installed uncomend:
# install.packages("httr")
# install.packages("jsonlite")


# Complete Database export via R-Studio into CSV
# For each measurement/data-point one CSV is created
# Node that this can take up to an hour depending on size internet speed.

require("httr")
require("jsonlite")

#options(digits=22)

start_time <- Sys.time()

# insert in your credential and URL
url_token <- 'https://<      insered the DNS here     >/?format=json'   # insert URL
url <- 'https://<      insered the DNS here     >/?format=json' #  insert URL
query <- list(
  username = jsonlite::unbox('******'), # Enter your username here.
  password = jsonlite::unbox('******') # Enter your password here.
)
max_rows <- 200000 #define maximum rows per query, ask Admin if needed!



# ---------------- #

# get Token
results_token <- POST(url_token, body = query,  encode = "json")
raw_token <- content(results_token)
prefix <-"Token"
token <- paste(prefix, raw_token, sep = " ")

# Get IoTree with all nodes and leafs.
Iotree <- GET(url, add_headers(Authorization = token), encode = "json")
# Make a request for your data and send it to the API.
strIotree <- content(Iotree, "text") # Choose one of the available gateways.
dfIotree<- fromJSON(strIotree, flatten = TRUE)
leafs <- dfIotree[["listofleafs"]]


#loop through all leafs -> download in chunks (of max row by server) and sore each leaf as csv.
errors = list()
for (leaf in leafs) {
  response_content <- list()
  curr_time_start <- 0
  continue <- TRUE
  dfall <- data.frame()
  while (continue){
    query <- list(
      tree = jsonlite::unbox(leaf), # insert the tree branch/id, example: ["gatewayself", "gateway2/sensor"]
      time_start = jsonlite::unbox(curr_time_start), # insert start time in UNIX-Time in ms
      time_end = jsonlite::unbox('now') # insert end time in UNIX-Time in ms. You can use "now" for current Server time.
    )
    results <- POST(url, add_headers(Authorization = token), body = query,  encode = "json")
    if (!(results[["status_code"]] = 200)){
      error <- c(results[["status_code"]], leaf)
      errors <- c(errors, error)      #appent errora to list errors
      continue = FALSE
      break
    }
    # check if response code 200!!!
    response_content <- content(results)
    respmatrix <- do.call(rbind, response_content[[1]][["posts_body"]])
    colnames(respmatrix) <- response_content[[1]][["posts_head"]]
    dfresp <- as.data.frame(respmatrix)
    dfall <- dplyr::bind_rows(dfall, dfresp)
    #get last time point and convert to unix-time format
    curr_time_start <- response_content[[1]][["posts_body"]][[length(response_content[[1]][["posts_body"]])]][[1]]
    curr_time_start <- as.numeric(as.POSIXct(curr_time_start, format = "%Y-%m-%dT%H:%M:%OS"))*1000
    if (length(response_content[[1]][["posts_body"]]) < max_rows){ 
      continue <- FALSE
    }
  }
  for (i in colnames(dfall)){
    dfall[[i]][sapply(dfall[[i]], is.null)] <- NA
    dfall[[i]] <- unlist(dfall[[i]])
  }
  filename <- chartr(old = "/", new = ".", leaf)
  filename <- paste(filename, "CSV", sep=".")
  write.csv2(dfall, file = filename, row.names = FALSE)
}


end_time <- Sys.time()
print(end_time - start_time) # Stopwatch to execute all.

