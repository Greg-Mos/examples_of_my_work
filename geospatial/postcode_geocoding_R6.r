# Check if the required packages are installed, if not install them
list_of_packages <- c("R6", "data.table", "stringr", "dplyr", "tibble", "sqldf", "docstring")
new_packages <- list_of_packages[!(list_of_packages %in% installed.packages()[,"Package"])]
if(length(new_packages)) install.packages(new_packages)

# Load required packages
lapply(list_of_packages, library, character.only = TRUE)

PostcodeGeocoder <- R6Class("PostcodeGeocoder",
                            public = list(
                              #' @field nspl_csv_regex Regular expression (regex) for automatically finding  
                              #' the National Statistics Postcode Lookup (NSPL) CSV in the current working directory (cwd)
                              nspl_csv_regex = "^(NSPL_).*20[2-9][0-9]_UK\\.csv$",
                              #' @field pcd_extract_regex Postcode extraction regex. Tested on the NSPL data. 
                              #' Achieves 100% extraction success for valid postcodes in NSPL columns "pcd" and "pcds".
                              pcd_extract_regex = "[A-Za-z][A-Ha-hJ-Yj-y]?[0-9][A-Za-z0-9]? {0,2}[0-9][A-Za-z]{2}|[Gg][Ii][Rr] ?0[Aa]{2}",
                              #' @field postcodes Will hold the NPSL data after initialisation, so 
                              #' subsequent geocodings won't require reading the NSPL CSV again. 
                              postcodes = NULL,
                              #' @field select Keep only the following columns from the NSPL CSV
                              select = c("pcds", "oseast1m", "osnrth1m", "pcd", "pcd2"),
                              initialize = function(nspl_csv = NA){
                                #' @description  PostcodeGeocoder takes UK postcodes and returns the corresponding
                                #' geographic coordinates as eastings and northings. It uses NSPL data. 
                                #' @param nspl_csv character. The file path of the National Statistics Postcode Lookup CSV file.
                                #' Defaults to NA, whence it searches the cwd for the first filename starting with "NSPL_" 
                                #' and ending with "20**_UK.csv"
                                #' @examples
                                #' post <- PostcodeGeocoder$new()
                                #' post <- PostcodeGeocoder$new(nspl_csv = "~/GIS/Postcodes/Data/NSPL_NOV_2021_UK.csv")
                                private$read_nspl(nspl_csv = nspl_csv)
                              },
                              extract_pcds = function(pcd_data, column){
                                #' @description  Extract postcodes from a specified postcode/address column in a CSV or dataframe 
                                #' @param pcd_data character or data.frame or tibble
                                #' The file path of the CSV file or a data frame or a tibble with postcodes/addresses
                                #' @param column character
                                #' The name of the postcode/address column 
                                #' @return A tibble with the extracted postcodes in a new column "pcds" and 
                                #' eastings and northings in new columns "oseast1m",	"osnrth1m"
                                #' @examples
                                #' post <- PostcodeGeocoder$new()
                                #' results <- post$extract_pcds(df, "postcodes")
                                #' results <- post$extract_pcds("~/GIS/Postcodes/data.csv", "Addresses")
                                tb <- private$get_data(pcd_data)
                                extracted_pcds <- stringr::str_extract(tb[[column]], self$pcd_extract_regex) %>%
                                  stringr::str_to_upper()
                                tb <- tibble::add_column(tb, ext_pcds = extracted_pcds)
                                return(tb)
                              },
                              geocode_pcds = function(pcd_data, column){
                                #' @description  Geocodes postcodes, after extracting them from a specified postcode/address column 
                                #' in a CSV or dataframe or tibble
                                #' @param pcd_data character or data.frame or tibble
                                #' The file path of the CSV file or a data frame or a tibble with postcodes/addresses
                                #' @param column character
                                #' The name of the postcode/address column 
                                #' @return A tibble with the extracted postcodes in a new column "pcds"
                                #' @examples
                                #' post <- PostcodeGeocoder$new()
                                #' results <- post$geocode_pcds(df, "postcodes")
                                #' results <- post$geocode_pcds("~/GIS/Postcodes/data.csv", "Addresses")
                                tb <- self$extract_pcds(pcd_data = pcd_data, column = column)
                                subpost <- self$postcodes %>%
                                  dplyr::filter((pcds %in% tb$ext_pcds) | 
                                                  (pcd %in% tb$ext_pcds) | 
                                                  (pcd2 %in% tb$ext_pcds))
                                tb_geo <- sqldf("SELECT * FROM
                                                tb LEFT JOIN subpost ON 
                                                tb.ext_pcds = subpost.pcds OR 
                                                tb.ext_pcds = subpost.pcd OR 
                                                tb.ext_pcds = subpost.pcd2") %>% 
                                  tibble::as_tibble()
                                return(tb_geo) 
                              }
                            ),
                            private = list(
                              get_data = function(pcd_data){
                                #' @description  Reads in data. Internal method for reading in data
                                #' @param pcd_data character or data.frame or tibble
                                #' A CSV filepath or a dataframe or a tibble
                                #' @return A tibble
                                if (! is.data.frame(pcd_data)){
                                  tb <- read.csv(file = pcd_data) 
                                } else{
                                  tb <- pcd_data
                                }
                                tb <- tibble::as_tibble(tb)
                                return(tb)
                              },
                              read_nspl = function(nspl_csv = NA){
                                #' @description  Internal method that is used in initialisation
                                #' @param nspl_csv character. The file path of the National Statistics Postcode Lookup CSV file.
                                #' Defaults to NA, whence it searches the cwd for the first filename starting with "NSPL_" 
                                #' and ending with "20**_UK.csv"
                                if (is.na(nspl_csv)){
                                  nspl_path <- dir(pattern=self$nspl_csv_regex)[1]
                                } else {
                                  nspl_path <- nspl_csv
                                }
                                self$postcodes <- fread(file = nspl_path, select = self$select) %>% 
                                  tibble::as_tibble()
                                self$postcodes$pcds <- stringr::str_trim(self$postcodes$pcds, side = "both")
                              }
                            )
                          )



