# Load required packages
list_of_packages <- c("R6", "data.table", "stringr", "dplyr", "tibble", "sqldf", "docstring", "lubirdate")

lapply(list_of_packages, library, character.only = TRUE)

PostcodeGeocoder <- R6Class("PostcodeGeocoder",
                            public = list(
                              #' @field nspl_csv_regex Regular expression (regex) for automatically finding  
                              #' the National Statistics Postcode Lookup (NSPL) CSV in the current working directory (cwd)
                              nspl_csv_regex = "^(NSPL_).*20[2-9][0-9]_UK\\.csv$",
                              #' @field pcd_extract_regex Postcode extraction regex. Tested on the NSPL data. 
                              #' Achieves 100% extraction success for valid postcodes in NSPL columns "pcd" and "pcds".
                              pcd_extract_regex = "[A-Za-z]{1,2}[0-9][A-Za-z0-9]? {0,2}[0-9][A-Za-z]{2}",
                              #' @field postcodes Will hold the NPSL data after initialisation, so 
                              #' subsequent geocodings won't require reading the NSPL CSV again. 
                              postcodes = NULL,
                              #' @field select Keep only the following columns from the NSPL CSV
                              nspl_cols = c("pcds","lat", "long"),
                              initialize = function(nspl_csv = NULL, add_nspl_cols = NULL){
                                #' @description  PostcodeGeocoder takes UK postcodes and returns the corresponding
                                #' geographic coordinates as eastings and northings. It uses NSPL data. 
                                #' @param nspl_csv character. The file path of the National Statistics Postcode Lookup CSV file.
                                #' Defaults to NA, whence it searches the cwd for the first filename starting with "NSPL_" 
                                #' and ending with "20**_UK.csv"
                                #' @param add_nspl_cols character. Additional columns to read import from NSPL.                                
                                #' @examples
                                #' post <- PostcodeGeocoder$new()
                                #' post <- PostcodeGeocoder$new(nspl_csv = "~/GIS/Postcodes/Data/NSPL_NOV_2021_UK.csv")
                                self$nspl_cols <- unique(c(self$nspl_cols, add_nspl_cols))
                                private$read_nspl(nspl_csv = nspl_csv)
                              },
                              extract_pcds = function(column, pcd_data = NULL){
                                #' @description  Extract postcodes from a specified postcode/address column in a CSV or dataframe 
                                #' @param column character
                                #' The name of the postcode/address column 
                                #' @param pcd_data character or data.frame or tibble
                                #' The file path of the CSV file or a data frame or a tibble with postcodes/addresses
                                #' Defaults to NULL, which brings up a file selection dialog box. 
                                #' @return A tibble with the extracted postcodes in a new column "ext_pcds"
                                #' @examples
                                #' post <- PostcodeGeocoder$new()
                                #' results <- post$extract_pcds("Postcode")
                                #' results <- post$extract_pcds("postcodes", df)
                                #' results <- post$extract_pcds("Addresses", "~/GIS/Postcodes/data.csv")
                                tb <- private$get_data(pcd_data)
                                extracted_pcds <- stringr::str_extract(tb[[column]], self$pcd_extract_regex)
                                tb <- tibble::add_column(tb, ext_pcds = extracted_pcds)
                                str_c("Extracted ", sum(!is.na(tb$ext_pcds)), " out of ", length(tb$ext_pcds), " postcodes") %>% print()
                                return(tb)
                              },
                              geocode_pcds = function(column, pcd_data = NULL){
                                #' @description  Geocodes postcodes, after extracting them from a specified postcode/address column 
                                #' in a CSV or dataframe or tibble
                                #' @param column character
                                #' The name of the postcode/address column 
                                #' @param pcd_data character or data.frame or tibble
                                #' The file path of the CSV file or a data frame or a tibble with postcodes/addresses
                                #' Defaults to NULL, which brings up a file selection dialog box.
                                #' @return A geocoded dataset
                                #' @examples
                                #' post <- PostcodeGeocoder$new()
                                #' results <- post$geocode_pcds("Postcode")
                                #' results <- post$geocode_pcds("postcodes", df)
                                #' results <- post$geocode_pcds("Addresses", "~/GIS/Postcodes/data.csv")
                                
                                # extract
                                tb <- self$extract_pcds(pcd_data = pcd_data, column = column) %>%
                                  dplyr::mutate(temp_pcd_key = stringr::str_to_upper(stringr::str_replace_all(ext_pcds, " ", "")))

                                
                                #filter
                                subpost <- self$postcodes %>% 
                                  dplyr::mutate(temp_pcd_key = stringr::str_to_upper(stringr::str_replace_all(pcds, " ", ""))) %>%
                                  dplyr::filter(temp_pcd_key %in% tb$temp_pcd_key) 
                                
                                #join
                                tb_geo <- dplyr::left_join(x = tb, y = subpost, by = "temp_pcd_key") %>% 
                                  dplyr::select(-temp_pcd_key) %>% tibble::as_tibble()
                                
                                str_c("Geocoded  ", sum(!is.na(tb_geo$lat)), " out of ", sum(!is.na(tb$ext_pcds)), " postcodes") %>% print()
                                
                                return(tb_geo) 
                              }
                            ),
                            private = list(
                              get_data = function(pcd_data = NULL){
                                #' @description  Reads in data. Internal method for reading in data
                                #' @param pcd_data character or data.frame or tibble
                                #' A CSV filepath or a dataframe or a tibble. Defaults to NA, where it brings up a file selection
                                #' dialog
                                #' @return A tibble
                                if (is.null(pcd_data)){
                                  file = nspl_path <- choose.files(multi = FALSE, 
                                                                   caption = "Select data csv",
                                                                   filters = matrix(c("Comma-separated values (*.csv)", "*.csv")))
                                  tb <- read.csv(file = file)
                                } else if (! is.data.frame(pcd_data)){
                                  tb <- read.csv(file = pcd_data) 
                                } else{
                                  tb <- pcd_data
                                }
                                tb <- tibble::as_tibble(tb)
                                return(tb)
                              },
                              read_nspl = function(nspl_csv = NULL){
                                #' @description  Internal method that is used in initialisation
                                #' @param nspl_csv character. The file path of the National Statistics Postcode Lookup CSV file.
                                #' Defaults to NULL, where it searches the cwd for the first filename starting with "NSPL_" 
                                #' and ending with "20**_UK.csv". If multiple NSPL files are found, it uses that with the most
                                #' recent date in its name.
                                
                                import_nspl <- function(nspl_path){
                                  self$postcodes <- fread(file = nspl_path, select = self$nspl_cols) %>% 
                                    tibble::as_tibble()
                                }
                
                                if (is.null(nspl_csv)){
                                  nspl_files <- dir(pattern=self$nspl_csv_regex) 
                                  nspl_dates <- nspl_files %>% stringr::str_sub(6, 13) %>% lubridate::my()
                                  nspl_path <- nspl_files[nspl_dates == max(nspl_dates)]
                                } else {
                                  nspl_path <- nspl_csv
                                }
                                
                                # allow the user to choose file interactively if the csv in not in cwd or specified path.
                                tryCatch(
                                  {
                                    import_nspl(nspl_path)
                                  },
                                  error=function(cond){
                                    message("NSPL csv could not be found")
                                    message("Select file interactively")
                                    nspl_path <- choose.files(multi = FALSE, 
                                                              caption = "Select NSPL csv",
                                                              filters = matrix(c("Comma-separated values (*.csv)", "*.csv")))
                                    
                                    import_nspl(nspl_path)
                                    
                                    message(c("Imported ", nspl_path))
                                  }
                                )
                                
                  
                                self$postcodes$pcds <- stringr::str_trim(self$postcodes$pcds, side = "both")
                              }
                            )
)


