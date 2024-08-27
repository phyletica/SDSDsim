#! /usr/bin/env Rscript

library(phytools)
library(yaml)

plot_SDSD_tree = function(tree, burst_times, states, state_colors, mar = NULL) {
    colors = setNames(state_colors, states)
    if (is.null(mar)) {
        p = plotSimmap(tree, colors, ftype = "off")
    }
    else {
        p = plotSimmap(tree, colors, ftype = "off", mar = mar)
    }
    n_tips = length(tree$tip.label)
    y_buffer = 0.05 * n_tips
    y_lims = c(-y_buffer, n_tips + y_buffer)
    for (time in burst_times) {
        lines(
              x = c(time, time),
              y = y_lims,
              lty = "dashed",
              lwd = 3.0,
              )
    }
    if (is.null(mar)) {
        p = plotSimmap(tree, colors, add = T, ftype = "off")
    }
    else {
        p = plotSimmap(tree, colors, add = T, ftype = "off", mar = mar)
    }
}

sd_trees = read_yaml("sd-trees.yml")

states = c("0", "1")
state_colors = c("black", "red")

tree_count = 0
for (tree in sd_trees$trees) {
    tree_count = tree_count + 1
    t = read.simmap(text = tree$tree, format = "phylip", rev.order = F)
    pdf(file = paste0('tree-', tree_count, '.pdf'))
    plot_SDSD_tree(t, tree$burst_times, states, state_colors)
    dev.off()
}

bd_trees = read_yaml("bd-trees.yml")

mar = c(2.1, 0.6, 0.6, 0.6)

ntrees = length(sd_trees)
pdf(file = 'all-trees.pdf')
par(mfrow = c(2, ntrees))
for (tree in sd_trees$trees) {
    t = read.simmap(text = tree$tree, format = "phylip", rev.order = F)
    plot_SDSD_tree(t, tree$burst_times, states, state_colors, mar = mar)
    axis(1, cex.axis=0.8)
}
for (tree in bd_trees$trees) {
    t = read.simmap(text = tree$tree, format = "phylip", rev.order = F)
    plot_SDSD_tree(t, tree$burst_times, states, state_colors, mar = mar)
    axis(1, cex.axis=0.8)
}
dev.off()
