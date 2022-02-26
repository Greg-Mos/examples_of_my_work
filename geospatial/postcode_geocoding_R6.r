#Check if the required packages are installed, if not install them
list_of_packages <- c("R6", "data.table", "stringr", "magrittr")
new_packages <- list_of_packages[!(list_of_packages %in% installed.packages()[,"Package"])]
if(length(new_packages)) install.packages(new_packages)

#Load required packages
lapply(list_of_packages, library, character.only = TRUE)

PostcodeGeocoder <- R6Class("PostcodeGeocoder",
                            public = list(
                              # Regex for automatically finding the 
                              # National Statistics Postcode Lookup (NSPL) csv in the cwd
                              nspl_csv_regex = "^(NSPL_).*20[2-9][0-9]_UK\\.csv$",
                              # Postcode extraction regex. Tested on the NSPL data. 
                              # Achieves 100% extraction success for valid postcodes in NSPL columns "pcd" and "pcds".
                              pcd_extract_regex = "[A-Za-z][A-Ha-hJ-Yj-y]?[0-9][A-Za-z0-9]? {0,2}[0-9][A-Za-z]{2}|[Gg][Ii][Rr] ?0[Aa]{2}",
                              # postcodes will hold the NPSL data after initialisation, so 
                              # subsequent geocodings won't require reading the NSPL csv again. 
                              postcodes = NULL,
                              # Keep only these columns from the NSPL csv
                              select = c("pcds", "pcd", "pcd2", "oseast1m", "osnrth1m"),
                              initialize = function(nspl_csv = NA){
                                # PostcodeGeocoder reads addresses or postcodes from csv and returns the corresponding
                                # geographic coordinates in eastings and northings in new columns. It uses the NSPL data. 
                                self$read_pcds(nspl_csv = nspl_csv)
                              },
                              read_pcds = function(nspl_csv = NA){
                                # Internal method that is used in initialisation
                                # Parameters
                                # ----------
                                # nspl_csv: character 
                                # The file path of the National Statistics Postcode Lookup csv file with all the UK postcodes,
                                # for example "~/GIS/Postcodes/Data/NSPL_NOV_2021_UK.csv"
                                # If NA then it searches the cwd for the first csv filename 
                                # starting with "NSPL_" and ending with "20**_UK.csv"
                                if (is.na(nspl_csv)){
                                  self$postcodes <- fread(file = dir(pattern=self$nspl_csv_regex)[1],
                                                          select = self$select)
                                } else {
                                  self$postcodes <- fread(file = nspl_csv,
                                                          select = self$select)
                                }
                                self$postcodes$pcds <- trimws(self$postcodes$pcds)
                              },
                              extract_pcds = function(pcd_data, column){
                                # Extracts postcodes from a specified address column in a csv
                                # Parameters
                                # ----------
                                # pcd_data: character or data.frame
                                # The file path of the csv file or a data frame with addresses
                                #
                                # column: character
                                # The name of the address column 
                                #
                                # Returns
                                # -------
                                # A data frame with the extracted postcodes in a new column "pcds"
                                df <- private$get_data(pcd_data)
                                df$pcds <- str_extract(df[[column]], self$pcd_extract_regex) %>%
                                  toupper()
                                return(df)
                              },
                              geocode_pcds = function(pcd_data, column, extract=FALSE){
                                # Geocodes postcodes, after optionally extracting them, 
                                # from a specified postcode/address column in a csv
                                # Parameters
                                # ----------
                                # pcd_data: character or data.frame
                                # The file path of the csv file or a data frame with postcodes/addresses
                                #
                                # column: character
                                # The name of the postcode/address column 
                                #
                                # Returns
                                # -------
                                # A data frame with eastings and northings in new columns 

                                if (extract){
                                  df <- self$extract_pcds(pcd_data = pcd_data, column = column)
                                } else {
                                  df <- private$get_data(pcd_data)
                                  df$pcds <- df[[column]] %>% toupper()
                                }
                                subpost <- self$postcodes[self$postcodes$pcds %in% df$pcds | self$postcodes$pcd %in% df$pcds 
                                                      | self$postcodes$pcd2 %in% df$pcds]
                                df_geo <- merge(x = df, y = subpost, by = "pcds", all.x = TRUE)
                                return(df_geo)
                              }
                            ),
                            private = list(
                              get_data = function(pcd_data){
                                # read in data
                                # Parameters
                                # ----------
                                # pcd_data: character or data.frame
                                # A csv filepath of a dataframe
                                # Returns
                                # ----------
                                # A dataframe
                                if (! "data.frame" %in% class(pcd_data)){
                                  df <- fread(file = pcd_data)
                                } else{
                                  df <- pcd_data
                                }
                                return(df)
                              }
                            )
                          )

