# Fill policy wheel cells by value category (0/1/2) within one combined wheel
fill_in_cells_combined <- function(p, df, wheel_opts) {
  policy_rows <- df[policy == p & !is.na(implemented), ]
  
  track_index <- wheel_opts[policy == p]$i
  
  for (i in seq_len(nrow(policy_rows))) {
    s <- policy_rows$state[i]
    val <- policy_rows$implemented[i]
    
    if (is.na(s) || !(s %in% get.all.sector.index())) next
    
    track_color <- if (val == 0) {
      wheel_opts[policy == p]$col_low
    } else if (val == 1) {
      wheel_opts[policy == p]$col_med
    } else if (val == 2) {
      wheel_opts[policy == p]$col_high
    } else {
      NA
    }
    
    if (is.na(track_color)) next
    
    draw.sector(
      get.cell.meta.data("cell.start.degree", sector.index = s),
      get.cell.meta.data("cell.end.degree", sector.index = s),
      rou1 = get.cell.meta.data("cell.top.radius", track.index = track_index),
      rou2 = get.cell.meta.data("cell.bottom.radius", track.index = track_index),
      col = track_color,
      border = NA
    )
  }
}