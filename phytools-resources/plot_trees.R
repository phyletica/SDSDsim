#! /usr/bin/env Rscript

library(phytools)
library(yaml)

plot_SDSD_tree = function(tree, burst_times, states, state_colors) {
    colors = setNames(state_colors, states)
    p = plotSimmap(tree, colors)
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
    p = plotSimmap(tree, colors, add = T)
}

data = read_yaml("out.yml")

states = c("0", "1")
state_colors = c("black", "red")

tree_count = 0
for (tree in data$trees) {
    tree_count = tree_count + 1
    t = read.simmap(text = tree$tree, format = "phylip", rev.order = F)
    pdf(file = paste0('tree-', tree_count, '.pdf'))
    plot_SDSD_tree(t, tree$burst_times, states, state_colors)
    dev.off()
}


t1 = read.simmap(file="tmp1.tre", format="phylip", rev.order=F)
t2 = read.simmap(file="tmp2.tre", format="phylip", rev.order=F)
t3 = read.simmap(file="tmp3.tre", format="phylip", rev.order=F)

colors = setNames(state_colors, states)

pdf(file="tmp1.pdf")
plotSimmap(t1, colors)
dev.off()

pdf(file="tmp2.pdf")
plotSimmap(t2, colors)
dev.off()

pdf(file="tmp3.pdf")
plotSimmap(t3, colors)
dev.off()
