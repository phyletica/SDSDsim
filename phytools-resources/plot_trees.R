#! /usr/bin/env Rscript

library(phytools)
library(yaml)

# How I got these colors from matplotlib:
# import matplotlib.cm
# v = matplotlib.cm.get_cmap("viridis")
# v(0.0, bytes = True)
viridis00 = rgb(68, 1, 84, max = 255)
# v(0.25, bytes = True)
viridis025 = rgb(58, 82, 139, max = 255)
# v(0.4, bytes = True)
viridis04 = rgb(41, 120, 142, max = 255)
# v(0.5, bytes = True)
viridis05 = rgb(32, 144, 140, max = 255)
# v(0.8, bytes = True)
viridis08 = rgb(121, 209, 81, max = 255)
# v(1.0, bytes = True)
viridis10 = rgb(253, 231, 36, max = 255)

dblue_col = rgb(90, 122, 148, max = 255)
lblue_col = rgb(142, 178, 209, max = 255)
dpurp_col = rgb(113, 74, 126, max = 255)
lpurp_col = rgb(182, 132, 199, max = 255)
dgreen_col = rgb(94, 141, 135, max = 255)
lgreen_col = rgb(138, 190, 183, max = 255)

plot_SDSD_tree = function(tree, burst_times, states, state_colors,
                          burst_line_color = dpurp_col, mar = NULL) {
    n_tips = length(tree$tip.label)
    y_buffer = 0.04 * n_tips
    y_lims = c(-y_buffer, n_tips + y_buffer)
    colors = setNames(state_colors, states)
    if (is.null(mar)) {
        p = plotSimmap(tree, colors, ftype = "off", ylim = y_lims)
    }
    else {
        p = plotSimmap(tree, colors, ftype = "off", ylim = y_lims, mar = mar)
    }
    for (time in burst_times) {
        lines(
              x = c(time, time),
              y = y_lims,
              lty = "dashed",
              lwd = 2.5,
              col = burst_line_color,
              )
    }
    if (is.null(mar)) {
        p = plotSimmap(tree, colors, add = T, ftype = "off", ylim = y_lims)
    }
    else {
        p = plotSimmap(tree, colors, add = T, ftype = "off", ylim = y_lims, mar = mar)
    }
}

sd_trees = read_yaml("sd-trees.yml")

states = c("0", "1")
# state_colors = c("black", viridis05)
state_colors = c("black", dblue_col)

tree_count = 0
for (tree in sd_trees$trees) {
    tree_count = tree_count + 1
    t = read.simmap(text = tree$tree, format = "phylip", rev.order = F)
    pdf(file = paste0('tree-', tree_count, '.pdf'))
    plot_SDSD_tree(t, tree$burst_times, states, state_colors)
    dev.off()
}

bd_trees = read_yaml("bd-trees.yml")

mar = c(0.69, 0.1, 0.01, 0.15)

ntrees = length(sd_trees)
pdf(file = 'all-trees.pdf', width = 15.5, height = 8.0)
par(mfrow = c(2, ntrees))
for (tree in sd_trees$trees) {
    t = read.simmap(text = tree$tree, format = "phylip", rev.order = F)
    plot_SDSD_tree(t, tree$burst_times_with_nodes, states, state_colors, mar = mar)
    n_tips = length(t$tip.label)
    y_bump = 0.055 * n_tips
    x_max = get("last_plot.phylo", envir=.PlotPhyloEnv)$x.lim[2]
    x_ticks = seq(0, floor(x_max), by = 1)
    if (x_max > 8) {
        x_ticks = seq(0, floor(x_max), by = 2)
    }
    axis(1, cex.axis = 1.6, pos = -y_bump, at = x_ticks)
}
for (tree in bd_trees$trees) {
    t = read.simmap(text = tree$tree, format = "phylip", rev.order = F)
    plot_SDSD_tree(t, tree$burst_times_with_nodes, states, state_colors, mar = mar)
    n_tips = length(t$tip.label)
    y_bump = 0.025 * n_tips
    x_max = get("last_plot.phylo", envir=.PlotPhyloEnv)$x.lim[2]
    x_ticks = seq(0, floor(x_max), by = 1)
    if (x_max > 8) {
        x_ticks = seq(0, floor(x_max), by = 2)
    }
    axis(1, cex.axis = 1.6, pos = -y_bump, at = x_ticks)
}
dev.off()
