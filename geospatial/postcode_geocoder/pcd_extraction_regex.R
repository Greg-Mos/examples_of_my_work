list_of_packages <- c("R6", "data.table", "stringr", "dplyr", "tibble", "sqldf", "docstring")
# Load required packages
lapply(list_of_packages, library, character.only = TRUE)

# read in all live uk postcodes from nspl
nspl_path <- "NSPL_NOV_2021_UK.csv"
uk_pcds <- fread(file = nspl_path, select = c("pcds", "doterm")) %>% 
  tibble::as_tibble() %>% filter(is.na(doterm))

# create two extra formats: 1. two spaces, 2. no spaces
uk_pcds <- uk_pcds %>% mutate(pcds_two_spaces = stringr::str_replace(pcds, " ", "  "), pcds_no_spaces = stringr::str_replace(pcds, " ", ""))

# UK postcode formats
# AA9A 9AA
# AA99 9AA	
# A9A 9AA		
# A99 9AA	
# AA9 9AA
# A9 9AA
# validation regex
validation_regex <- "^[A-Z]{1,2}[0-9][A-Z0-9]? {0,2}[0-9][A-Z]{2}$"

val_pcds <- uk_pcds %>% mutate(ext_pcds = stringr::str_extract(uk_pcds$pcds, validation_regex),
                               ext_pcds_two_spaces = stringr::str_extract(uk_pcds$pcds_two_spaces, validation_regex),
                               ext_pcds_no_spaces = stringr::str_extract(uk_pcds$pcds_no_spaces, validation_regex))
                               
                               
val_pcds[is.na(val_pcds$ext_pcds), ][, c("pcds", "ext_pcds", "doterm")]
val_pcds[is.na(val_pcds$ext_pcds_two_spaces), ][, c("pcds_two_spaces", "ext_pcds_two_spaces", "doterm")]
val_pcds[is.na(val_pcds$ext_pcds_no_spaces), ][, c("pcds_no_spaces", "ext_pcds_no_spaces", "doterm")]

# extraction test function
test_extr <- function(format, n){
  # extraction regex
  extraction_regex <- "[A-Z]{1,2}[0-9][A-Z0-9]? {0,2}[0-9][A-Z]{2}"
  
  sample_pcds <- sample(uk_pcds[[format]], n)
  
  excerpt = "The outward code is the first half of a postcode (before the space). Some are non-geographic, i.e. does not divulge the location.
Distinguishing features include:
2-4 characters long
Always begins with a letter
May end with a number or letter"
  
  
  end <- as.integer(runif(n, 1, str_length(excerpt)))
  end2 <- as.integer(runif(n, 1, str_length(excerpt))) * (-1)  
  
  test_adrs <- str_c(str_sub(excerpt, 1, end), sample_pcds ,str_sub(excerpt, -end2), sep = " ")
  
  ext <- stringr::str_extract(test_adrs, extraction_regex)
  
  return(ext)
}

# one space
test_extr("pcds", 1000)
# two spaces
test_extr("pcds_two_spaces", 1000)
# no spaces
test_extr("pcds_no_spaces", 1000)

