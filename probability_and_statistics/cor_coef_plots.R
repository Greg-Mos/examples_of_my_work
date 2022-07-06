library(tidyverse)

correlation <- function(r, sigmax = 2, sigmay = 1, n = 3000){
  m <- (r * sigmay) / sigmax
  sigmaz <- sqrt(sigmay^2 - m^2 * sigmax^2)
  x <- rnorm(n, mean = 0, sd = sigmax)
  z <- rnorm(n, mean = 0, sd = sigmaz)
  y <- m * x + z
  data <- tibble(x = x, y = y)
  plot(ggplot(data = data) +
         geom_hline(yintercept = 0, color = "gray", size = 1) +
         geom_vline(xintercept = 0, color = "gray", size = 1) +
         geom_point(mapping = aes(x = x, y = y)) +
         theme_light() 
       ) 
  
  return(data)
}