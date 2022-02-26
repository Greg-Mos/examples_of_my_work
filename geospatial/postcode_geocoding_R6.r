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
                              pcd_file_regex = "^(NSPL_).*20[2-9][0-9]_UK\\.csv$",
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
                                  self$postcodes <- fread(file = dir(pattern=self$pcd_file_regex)[1],
                                                          select = self$select)
                                } else {
                                  self$postcodes <- fread(file = nspl_csv,
                                                          select = self$select)
                                }
                                self$postcodes$pcds <- trimws(self$postcodes$pcds)
                              },
                              extract_pcds = function(data_file, column){
                                # Extracts postcodes from a specified address column in a csv
                                # Parameters
                                # ----------
                                # data_file: character 
                                # The file path of the csv file with the addresses
                                #
                                # column: character
                                # The name of the address column 
                                #
                                # Returns
                                # -------
                                # A data frame with the extracted postcodes in a new column "pcds"
                                data <- fread(file = data_file)
                                data$pcds <- str_extract(data[[column]], self$pcd_extract_regex) %>%
                                  toupper()
                                return(data)
                              },
                              geocode_pcds = function(data_file, column, extract=FALSE){

                                if (extract){
                                  data <- self$extract_pcds(data_file = data_file, column = column)
                                } else {
                                  data <- fread(file = data_file)
                                  data$pcds <- data[[column]] %>% toupper()
                                }
                                subpost <- self$postcodes[self$postcodes$pcds %in% data$pcds | self$postcodes$pcd %in% data$pcds 
                                                      | self$postcodes$pcd2 %in% data$pcds]
                                data_with_geo <- merge(x = data, y = subpost, by = "pcds", all.x = TRUE)
                                return(data_with_geo)
                              }
                            )
                          )


