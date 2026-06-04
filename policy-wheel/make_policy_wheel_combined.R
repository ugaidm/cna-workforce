plot_policy_wheel_combined <- function(data,
                                       policies = NULL,
                                       state_var = "state",
                                       plot_width = 15,
                                       plot_height = 15,
                                       out_file = NULL) {
  
  if (any(!(policies %in% names(data)))) {
    stop("make sure all values in `policies` are variable names in your data.")
  }
  
  # remove DC and US from the wheel
  states <- c("OH", "WI", "DE", "FL", "GA", "MD", "NC", "SC", "VA", "WV", "IA",
              "KS", "MN", "MO", "NE", "ND", "SD", "AL", "KY", "MS", "TN", "AR", "LA",
              "OK", "TX", "AZ", "CO", "ID", "MT", "NV", "NM", "UT", "WY", "CA", "OR",
              "WA", "AK", "HI", "CT", "ME", "MA", "NH", "RI", "VT", "NY", "NJ", "PA",
              "IL", "IN", "MI")
  
  df <- as.data.frame(data)[c(state_var, policies)]
  df <- melt(setDT(df), id.vars = state_var, variable.name = "policy", value.name = "implemented")
  names(df)[names(df) == state_var] <- "state"
  df[, implemented := as.numeric(implemented)]
  df <- df[!is.na(implemented), ]
  df <- df[!state %in% c("US", "DC"), ]
  
  wheel_opts <- data.table(
    policy = policies,
    i = seq_along(policies),
    
    col_low = c(
      "#c6dbef",  # Age
      "#fdd0a2",  # Race
      "#fff7bc",  # School
      "#c7e9c0",  # Wages
      "#dadaeb"   # Marital Status
    ),
    
    col_med = rep("#FFFFFF", length(policies)),
    
    col_high = c(
      "#2171b5",  # Age
      "#e6550d",  # Race
      "#d4a017",  # School
      "#238b45",  # Wages
      "#6a51a3"   # Marital Status
    )
  )
  
  if (!is.null(out_file)) {
    if (grepl("\\.svg$", out_file)) {
      svg(filename = out_file, width = plot_width, height = plot_height)
    } else if (grepl("\\.pdf$", out_file)) {
      pdf(filename = out_file, width = plot_width, height = plot_height)
    } else if (grepl("\\.png$", out_file)) {
      png(filename = out_file, width = plot_width, height = plot_height, res = 300)
    } else {
      stop("Only .svg, .png, and .pdf are supported.")
    }
  }
  
  layout(
    matrix(c(1,
             2,
             3,
             4), ncol = 1, byrow = TRUE),
    heights = c(1.0, 6.5, 3.8, 1.6)
  )
  
  # title
  par(mar = c(0, 0, 0, 0))
  plot.new()
  text(0.5, 0.55, "CNA Demographics by State", cex = 3.7, font = 2)
  
  # wheel
  plot_policy_wheel_combined_internal(states, df, wheel_opts, policies)
  
  # --- Legend panel ---
  par(mar = c(1, 2, 1, 2))
  plot.new()
  plot.window(xlim = c(0, 1), ylim = c(0, 1))
  
  # Define equal-width columns
  low_x  <- 0.38
  med_x  <- 0.58
  high_x <- 0.78
  
  box_width <- 0.16
  half_w <- box_width / 2
  
  # Headers centered above boxes
  text(low_x,  0.93, "Below",    font = 2, cex = 2.35)
  text(med_x,  0.93, "Within Average Range", font = 2, cex = 2.35)
  text(high_x, 0.93, "Above",   font = 2, cex = 2.35)
  
  y_positions <- seq(0.80, 0.16, length.out = length(policies))
  
  low_labels  <- c("Younger", "Asian", "N/A", "Lower wages", "N/A")
  med_labels  <- c("40 years", "White", "HS diploma", "$35,294", "Unmarried")
  high_labels <- c("Older", "Black", "Associate's", "Higher wages", "Married")
  
  for (j in seq_along(policies)) {
    y <- y_positions[j]
    
    # Policy name
    text(0.08, y, labels = policies[j], adj = 0, cex = 2.35)
    
    # Equal-sized boxes
    rect(low_x  - half_w, y - 0.065, low_x  + half_w, y + 0.065,
         col = wheel_opts$col_low[j], border = "gray40", lwd = 1.2)
    
    rect(med_x  - half_w, y - 0.065, med_x  + half_w, y + 0.065,
         col = wheel_opts$col_med[j], border = "gray40", lwd = 1.2)
    
    rect(high_x - half_w, y - 0.065, high_x + half_w, y + 0.065,
         col = wheel_opts$col_high[j], border = "gray40", lwd = 1.2)
    
    # Centered text inside boxes
    text(low_x,  y, low_labels[j],  cex = 2.15, col = "black", font = 2)
    text(med_x,  y, med_labels[j],  cex = 2.10, col = "black", font = 2)
    text(high_x, y, high_labels[j], cex = 2.12, col = "white", font = 2)
  }
  
  # --- Note panel ---
  par(mar = c(1, 1, 1, 1))  # reduce side margins so box can stretch
  plot.new()
  plot.window(xlim = c(0, 1), ylim = c(0, 1))
  
  # Wider box (nearly full width)
  rect(0.01, 0.08, 0.99, 0.92, col = "#f9f9f9", border = "gray80", lwd = 1.2)
  
  # Title
  text(
    0.02, 0.78,
    labels = "Note:",
    adj = 0,
    font = 2,
    cex = 2.2
  )
  
  # Wrapped text with better line width
  note_text <- paste(
    "",
    "White boxes indicate ranges that are within 2 standard deviations of the national average.",
    "Colored boxes represent values below or above 2 standard deviations of the national average.",
    "Below and Above may also correspond to the least and most common deviations from the national average",
    "for variables that are text-based, not numeric, such as Race and Marital Status."
  )
  
  text(
    0.02, 0.45,
    labels = paste(strwrap(note_text, width = 95), collapse = "\n"),
    adj = 0,
    cex = 2.05
  )
  
  if (!is.null(out_file)) {
    invisible(dev.off())
  }
}