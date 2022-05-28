# Check if the required packages are installed, if not install them
list_of_packages <- c("dplyr", "tibble", "sqldf", "tictoc")
new_packages <- list_of_packages[!(list_of_packages %in% installed.packages()[,"Package"])]
if(length(new_packages)) install.packages(new_packages)

# Load required packages
lapply(list_of_packages, library, character.only = TRUE)

# read in test data
postcodes <- read.csv(file = "pg_test_nspl.csv") %>% tibble::as_tibble()
post <- read.csv(file = "pg_test_data.csv") %>% tibble::as_tibble()

# sql join 
tb_geo1 <- sqldf("SELECT * FROM
                 post LEFT JOIN postcodes ON 
                 post.pcds = postcodes.pcd1 OR 
                 post.pcds = postcodes.pcd2 OR 
                 post.pcds = postcodes.pcd3") %>% tibble::as_tibble()



# R code only
post2 <- tibble::add_column(post, temp_index = 1:length(post$pcds))
tb1 <- dplyr::inner_join(x = post2, y = postcodes, by = c("pcds" = "pcd1"), keep=TRUE)
tb2 <- dplyr::inner_join(x = post2, y = postcodes, by = c("pcds" = "pcd2"), keep=TRUE) 
tb3 <- dplyr::inner_join(x = post2, y = postcodes, by = c("pcds" = "pcd3"), keep=TRUE) 
tb4 <- union(tb1, tb2) %>% union(tb3)
tb5 <- dplyr::anti_join(x = post, y = tb4, by = "pcds", keep=TRUE)
tb_geo2 <- dplyr::bind_rows(tb4, tb5) %>% select(-(temp_index))



# R code only 2
match <- function(pcds, postcodes, coordinate){
  result <- pull(postcodes[postcodes$pcd1 == pcds | postcodes$pcd2 == pcds | postcodes$pcd3 == pcds, coordinate])
  if (length(result) == 0){
    return(NA)
  } else {
    return(result)
  }
}

east <- mapply(match, post$pcds, MoreArgs = list(postcodes = postcodes, coordinate = "easting"))
north <- mapply(match, post$pcds, MoreArgs = list(postcodes = postcodes, coordinate = "northing"))  

tb_geo3 <- tibble::add_column(post, easting = east, northing = north)


print(tb_geo1)
print(tb_geo2)
print(tb_geo3)
