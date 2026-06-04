# loading packages
suppressPackageStartupMessages(library(circlize))
library(data.table)
library(plyr)
library(lubridate)
library(openxlsx)

# setting WD
setwd("C:/Users/maw13321/Documents/GitHub/CNA-policy-wheel/R")

# loading functions
source("fill_in_cells.R")
source("make_policy_wheel.R")
source("plot_policy_wheel_internal.R")

# reading in a data frame where rows are states, columns are policies, and values are enactment dates

# Values can come in the forms: 0, 1, or 2 - 1 is the National Average, 0 is either 2 standard deviations under or least common difference, 2 means 2 standard deviations above or most common difference
df_wide <- read.xlsx("../Data/processed/CNA Variables Wheel.xlsx")
df_wide$state[df_wide$state == "NATIONAL"] <- "US"
names(df_wide) <- gsub("\\.", " ", names(df_wide))

is_full_state <- df_wide$state %in% state.name
df_wide$state[is_full_state] <- state.abb[match(df_wide$state[is_full_state], state.name)]

# looking at the data
head(df_wide)
unique(df_wide$state[is.na(df_wide$state)])
setdiff(unique(df_wide$state), c(state.abb, "DC", "US"))

# generating policy wheels
plot_policy_wheels(data = df_wide,
                   
                   # ordering policies by name:
                   policies = c("Age", "Percent White", "Percent HS Diploma", "Wages", "Percent Married"),
                   
                   # name of the state variable
                   state_var = "state",
                   
                   # restrict to relevant policy intervals, for locations that implemented the policy
                   policy_intervals = c(0, 1, 2),
                   plot_colors = c("#1f77b4", "#ff7f0e", "#FFFF00", "#dab8e5", "#9467bd"),
                   legend_args = list(x = "center", xjust = 0.5, y.intersp = 1.3, x.intersp = 1.3, cex = 2.5, pt.cex = 2.7, bty = "n", ncol = 2),
                   
                   panel_width = 4,
                   panel_height = 5,
                   
                   # where should the graph be saved?
                   out_file = "www/policy_wheel_1.svg")

# displaying the new graph
knitr::include_graphics("www/policy_wheel_1.svg")


# Changed to HHS Regions - if want old region breakdown, take "_hhs_regions" out of file types below
# loading functions for combined wheel
source("fill_in_cells_one_chart.R")
source("plot_policy_wheel_combined_internal_hhs_regions.R")
source("make_policy_wheel_combined_hhs_regions.R")

# generating combined policy wheels
plot_policy_wheel_combined(
  data = df_wide,
  policies = c("Age", "Percent White", "Percent HS Diploma", "Wages", "Percent Married"),
  state_var = "state",
  plot_width = 16,
  plot_height = 16,
  out_file = "www/policy_wheel_combined.svg"
)

# displaying the new graph
knitr::include_graphics("www/policy_wheel_combined.svg")