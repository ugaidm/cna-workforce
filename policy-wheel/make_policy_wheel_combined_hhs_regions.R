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
  states <- c("MN", "OH", "WI", "AR", "LA", "NM", "OK", "TX", "IA", "KS", "MO", "NE", "CO", "MT", "ND", "SD", "UT", "WY",
              "AZ", "CA", "HI", "NV", "AK", "ID", "OR", "WA", "CT", "ME", "MA", "NH", "RI", "VT", "NY", "NJ", "DE", "MD",
              "PA", "VA", "WV", "AL", "FL", "GA", "KY", "MS", "NC", "SC", "TN", "IL", "IN", "MI")
  
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
  text(low_x,  0.93, "Lower",    font = 2, cex = 2.35)
  text(med_x,  0.93, "Average", font = 2, cex = 2.35)
  text(high_x, 0.93, "Higher",   font = 2, cex = 2.35)
  
  y_positions <- seq(0.80, 0.16, length.out = length(policies))
  
  low_labels  <- c("39 or younger", "< 50%", "< 68%", "< $35,294", "< 43%")
  med_labels  <- c("40 years", "50 - 52%", "68 - 70%", "$35,294", "43 - 45%")
  high_labels <- c("41 or older", "> 52%", "> 70%", "> $35,294", "> 45%")
  
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
  
  # Centered box
  left <- 0.15
  right <- 0.85

  rect(
    left, -0.05,
    right, 0.9, 
    col = "#f9f9f9", border = "gray80", lwd = 1.2)
 
  # Midpoint of box
  mid_x <- (left + right) / 2
   
  # Title
  text(
    mid_x, 0.78,
    labels = "Note:",
    adj = 0.5,
    font = 2,
    cex = 2.2
  )
  
  # Wrapped text with better line width
  note_text <- paste(
    "White boxes indicate ranges that are within 2 standard deviations of the national average.",
    "Colored boxes represent values below or above 2 standard deviations of the national average. Percent high school diploma means percent of CNAs surveyed for whom a high school diploma or certificate is their highest level of education completed."
  )
  
  text(
    mid_x, 0.35,
    labels = paste(strwrap(note_text, width = 90), collapse = "\n"),
    adj = 0.5,
    cex = 2.05
  )
  
  if (!is.null(out_file)) {
    invisible(dev.off())
  }
}