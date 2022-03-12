clark_obs <- c(229, 211, 93, 35, 7, 1)
clark_exp <- c(226.74, 211.39, 98.54, 30.62, 7.14, 1.57)

clark_Xsq <- chisq.test(clark_obs, p = clark_exp, rescale.p = TRUE)

print(clark_Xsq)
# Chi-squared test for given probabilities
# 
# data:  clark_obs
# X-squared = 1.1709, df = 5, p-value = 0.9476

print(pchisq(clark_Xsq$statistic, df = 4, lower.tail = FALSE))
# X-squared 
# 0.8828615 



shaw_obs <- c(237, 189, 115, 28, 6, 1)
shaw_exp <- c(228.72, 211.25, 97.56, 30.03, 6.94, 1.50)

shaw_Xsq <- chisq.test(shaw_obs, p = shaw_exp, rescale.p = TRUE)

print(shaw_Xsq)
# Chi-squared test for given probabilities
# 
# data:  shaw_obs
# X-squared = 6.1921, df = 5, p-value = 0.288

print(pchisq(shaw_Xsq$statistic, df = 4, lower.tail = FALSE))
# X-squared 
# 0.1852571 
