plot_policy_wheel_combined_internal <- function(states, df, wheel_opts, policies) {
  par(mai = c(0.4, 0.4, 0.4, 0.4), xpd = TRUE)
  circos.clear()
  circos.par(cell.padding = c(0, 0, 0, 0))
  
  circos.initialize(factors = states, xlim = c(0, 1))
  
  # one track per policy
  replicate(length(policies), circos.track(ylim = c(0, 1), track.height = 0.085), simplify = FALSE)
  
  # state labels
  for (s in unique(states)) {
    highlight.sector(
      sector.index = s,
      track.index = 1,
      text = s,
      padding = c(-0.15, 1, 2.35, 1),
      cex = 2,
      text.vjust = 0.5,
      col = NA,
      border = NA,
      facing = "downward"
    )
  }
  
  # center labels
  text(0,  0.18, labels = "CNA",    cex = 2.55, font = 2)
  text(0,  0.00, labels = "Demographics", cex = 2.55, font = 2)
  text(0, -0.18, labels = "By State",   cex = 2.55, font = 2)
  
  # divider lines between regions
  for (s in c("CT", "NY", "IL", "DE", "IA", "AL", "AR", "AZ", "CA")) {
    circos.segments(
      x0 = -0.10,
      y0 = 0,
      x1 = -0.07,
      y1 = (1.42 * length(policies)),
      lwd = 2.6,
      sector.index = s
    )
  }
  
  # region labels
  highlight.sector(
    sector.index = c("CT", "ME", "MA", "NH", "RI", "VT"),
    track.index = 1,
    text = "New England",
    padding = c(1, 0, 6.5, 0),
    cex = 1.75,
    font = 2,
    border = NA,
    col = NA,
    facing = "bending.inside"
  )
  
  highlight.sector(
    sector.index = c("NY", "NJ", "PA"),
    track.index = 1,
    text = "Mid-Atlantic",
    padding = c(1, 0, 6.5, 0),
    cex = 1.75,
    font = 2,
    border = NA,
    col = NA,
    facing = "bending.inside"
  )
  
  highlight.sector(
    sector.index = c("IL", "IN", "MI", "OH", "WI"),
    track.index = 1,
    text = "East North Central",
    padding = c(1, 0, 6.5, 0),
    cex = 1.75,
    font = 2,
    border = NA,
    col = NA,
    facing = "bending.inside"
  )
  
  highlight.sector(
    sector.index = c("DE", "FL", "GA", "MD", "NC", "SC", "VA", "WV"),
    track.index = 1,
    text = "South Atlantic",
    padding = c(1, 0, 6.5, 0),
    cex = 1.75,
    font = 2,
    border = NA,
    col = NA,
    facing = "bending.inside"
  )
  
  highlight.sector(
    sector.index = c("IA", "KS", "MN", "MO", "NE", "ND", "SD"),
    track.index = 1,
    text = "West North Central",
    padding = c(1, 0, 6.5, 0),
    cex = 1.75,
    font = 2,
    border = NA,
    col = NA,
    facing = "bending.inside",
    text.vjust = .75
  )
  
  highlight.sector(
    sector.index = c("AL", "KY", "MS", "TN"),
    track.index = 1,
    text = "East South Central",
    padding = c(1, 0, 6.5, 0),
    cex = 1.75,
    font = 2,
    border = NA,
    col = NA,
    facing = "bending.inside"
  )
  
  highlight.sector(
    sector.index = c("AR", "LA", "OK", "TX"),
    track.index = 1,
    text = "West South Central",
    padding = c(1, 0, 6.5, 0),
    cex = 1.75,
    font = 2,
    border = NA,
    col = NA,
    facing = "bending.inside"
)
  
  highlight.sector(
    sector.index = c("AZ", "CO", "ID", "MT", "NV", "NM", "UT", "WY"),
    track.index = 1,
    text = "Mountain",
    padding = c(1, 0, 6.5, 0),
    cex = 1.75,
    font = 2,
    border = NA,
    col = NA,
    facing = "bending.inside"
  )
  
  highlight.sector(
    sector.index = c("CA", "OR", "WA", "AK", "HI"),
    track.index = 1,
    text = "Pacific",
    padding = c(1, 0, 6.5, 0),
    cex = 1.75,
    font = 2,
    border = NA,
    col = NA,
    facing = "bending.inside"
  )
  
  # fill rings
  lapply(policies, fill_in_cells_combined, df = df, wheel_opts = wheel_opts)
  
  circos.clear()
}