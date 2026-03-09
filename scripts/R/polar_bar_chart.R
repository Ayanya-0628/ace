# ============================================================
# 极坐标柱状图（Polar Bar Chart / Circular Bar Plot）
# 
# 用途：使用 circlize 包绘制环形柱状图，适用于多品种/多分组数据可视化
# 依赖：circlize, readxl, grid, showtext
# 输入：Excel 文件，需含 category, variety/variety_id, group, value, significance 列
# 输出：PDF 文件，3×2 子图排版
#
# 使用方法：
#   1. 修改下方 data_path 为你的 Excel 文件路径
#   2. 修改 pdf_path 为输出 PDF 路径
#   3. 修改 target_levels 为你的类别列表
#   4. 运行脚本
# ============================================================

# ============================================================
# 1. 环境准备与字体加载 (核心修复步骤)
# ============================================================
library(circlize)
library(readxl)
library(grid)
library(showtext) # 必须加载

# --- 关键：手动注册 Times New Roman 字体 ---
font_add("Times", 
         regular = "times.ttf", 
         bold = "timesbd.ttf", 
         italic = "timesi.ttf", 
         bolditalic = "timesbi.ttf")

# 开启 showtext 自动渲染 
showtext_auto()

# ============================================================
# 2. 数据读取与预处理 (★ 修改此处参数 ★)
# ============================================================
data_path <- "C:/Users/张银/Desktop/垩白粒率.xlsx"   # ← 修改为你的数据路径
pdf_path  <- "C:/Users/张银/Desktop/稻米品质分析图.pdf"  # ← 修改为输出路径

data <- readxl::read_xlsx(data_path)

# --- 提取品种列 ---
if ("variety_id" %in% colnames(data)) {
  data$variety <- data$variety_id
} else if (ncol(data) >= 5) {
  colnames(data)[5] <- "variety"
} else {
  stop("Excel中未找到品种列！")
}

variety_list <- unique(data$variety)
variety_list <- variety_list[!is.na(variety_list) & variety_list != ""]
num_varieties <- length(variety_list)

if (num_varieties == 0) stop("未检测到有效品种数据！")

# --- 数据预处理 ---
# ★ 修改为你的类别列表 ★
target_levels <- c("TYHZ", "YXYLS", "HY73", "YLY900", "WLY898", "FYXZ", "ELY603", "FLYX1H", "CLYHZ", "TY390", "YXY2115", "ELY2300", "YLYMXXZ", "WY308", "XZX24H", "YHSM", "ZJZ17", "HHZ", "WSSM", "GC2H", "XZX45H", "HH31H", "YZX", "EZ18", "LYZ", "EZ5H", "JKSM5H", "MXZ2H", "XZX32H", "NX42", "XYXZ", "YD6H/9311", "ZZ35", "LJZ")
data$category <- factor(data$category, levels = target_levels)
data <- data[!is.na(data$category) & data$category != "", ]

# --- 颜色准备 ---
if ("group" %in% colnames(data)) {
  unique_groups <- unique(data$group)
  unique_groups <- unique_groups[!is.na(unique_groups)]
  group_colors <- setNames(rainbow(length(unique_groups)), unique_groups)
} else {
  stop("Excel中缺少 'group' 列！")
}

bg_colors <- setNames(
  colorRampPalette(c("#4E79A7", "#F2F2B2", "#E15759", "#76B7B2"))(length(target_levels)),
  target_levels
)

# ============================================================
# 3. 定义绘图函数 (引入 current_levels 参数以支持拆分子图)
# ============================================================
# 【关键修改】：新增 current_levels 参数，仅接收当前子图分配到的最多 6 个品种
draw_variety_plot <- function(subset_data, variety_name, current_levels) {
  circos.clear()
  
  circos.par(
    start.degree = 90, 
    gap.degree = 10, 
    track.margin = c(0.01, 0.01), 
    cell.padding = c(0, 0, 0, 0)
  )
  
  # 使用拆分后的 current_levels 初始化 6 个扇区
  circos.initialize(factors = current_levels, xlim = c(0, 1))
  
  # --- 轨道 1：扇区标签 ---
  circos.track(
    ylim = c(0, 1), 
    track.height = 0.1, 
    bg.col = bg_colors[current_levels], # 提取当前 6 个品种对应的颜色
    panel.fun = function(x, y) {
      text_with_spaces <- gsub("(?<=.)(?=.)", "", CELL_META$sector.index, perl = TRUE)
      circos.text(
        CELL_META$xcenter, CELL_META$ycenter, text_with_spaces,
        facing = "bending.inside", niceFacing = TRUE,
        cex = 2.5, font = 1, col = "black", 
        family = "Times"
      )
    }
  )
  
  # --- 轨道 2：条形图 ---
  circos.trackPlotRegion(
    factors = current_levels, 
    ylim = c(0, 1), 
    track.height = 0.5, 
    bg.col = adjustcolor(bg_colors[current_levels], alpha.f = 0.2), 
    panel.fun = function(x, y) {
      sector_data <- subset_data[subset_data$category == CELL_META$sector.index, ]
      
      if (nrow(sector_data) > 0) {
        local_max <- max(sector_data$value, na.rm = TRUE) * 1.15
        if(is.na(local_max) || local_max <= 0) local_max <- 1 # 容错处理
        
        grid_at_real <- pretty(c(0, local_max), n = 4)
        grid_at_real <- grid_at_real[grid_at_real <= local_max]
        grid_at_norm <- grid_at_real / local_max
        
        for(h_norm in grid_at_norm) {
          circos.lines(x = c(0, 1), y = c(h_norm, h_norm), col = "grey80", lty = 2, lwd = 1)
        }
        
        # 坐标轴数字 
        circos.text(
          x = rep(0, length(grid_at_real)),
          y = grid_at_norm,
          labels = grid_at_real,
          facing = "reverse.clockwise",
          niceFacing = TRUE,
          adj = c(0.5, 1.2),
          cex = 2.5,
          col = "black",
          family = "Times" 
        )
        
        bar_width <- 0.2
        gap_width <- 0.1
        n_bars <- nrow(sector_data)
        sector_x_start <- CELL_META$xlim[1]
        sector_x_end <- CELL_META$xlim[2]
        total_available_width <- sector_x_end - sector_x_start - 2 * gap_width
        
        if (n_bars > 0) {
          bar_width <- total_available_width / (n_bars + (n_bars - 1) * gap_width / bar_width)
        }
        
        for (i in 1:n_bars) {
          xleft <- sector_x_start + gap_width + (i - 1) * (bar_width + gap_width)
          xright <- xleft + bar_width
          ytop <- sector_data$value[i] / local_max
          
          current_group <- as.character(sector_data$group[i])
          bar_color <- group_colors[current_group]
          
          circos.rect(
            xleft = xleft, ybottom = 0, xright = xright, ytop = ytop,
            col = bar_color, border = "black", lwd = 1
          )
          
          if (!is.na(sector_data$significance[i])) {
            circos.text(
              x = (xleft + xright) / 2, y = ytop + 0.02, 
              labels = sector_data$significance[i],
              col = "black", cex = 3, font = 2, 
              facing = "inside", niceFacing = TRUE, adj = c(0.5, 0),
              family = "Times" 
            )
          }
        }
      }
    }
  )
  
  # --- 圆心文字 ---
  text(0, 0, labels = variety_name, cex = 2, font = 2, col = "black", family = "Times") 
  
  circos.clear()
}


# ============================================================
# 4. 排版与导出 (按 3列2行 排版单页PDF，将品种拆分为独立子图)
# ============================================================

# 固定子图排版布局为：3列 2行
n_cols <- 3
n_rows <- 2

# 高度额外加了 2.0 是为了在整个页面的最底部给图例留出专门的空间，不挤占图形
pdf(file = pdf_path, width = 8 * n_cols, height = 8 * n_rows + 2)
showtext_begin()

# --- 核心拆分逻辑：每 6 个品种(target_levels) 为一组 ---
chunk_size <- 6
num_chunks <- ceiling(length(target_levels) / chunk_size)

for (i in 1:num_varieties) {
  variety_name <- variety_list[i]
  subset_data <- data[data$variety == variety_name, ]
  
  # 每一大组数据设置 3x2 的排版网格
  layout_matrix <- matrix(1:(n_rows * n_cols), nrow = n_rows, ncol = n_cols, byrow = TRUE)
  layout(mat = layout_matrix)
  
  # 设置画布边缘：oma(底, 左, 上, 右) 中的底部预留大面积空白绘制统一图例
  par(oma = c(6, 0, 0, 0), mar = c(1, 1, 1, 1), xpd = TRUE) 
  
  # --- 循环绘制拆分后的 6 个子图 ---
  for (chunk_idx in 1:num_chunks) {
    # 提取当前子图需要画的 6 个品种 (最后一图可能只有5个)
    start_idx <- (chunk_idx - 1) * chunk_size + 1
    end_idx <- min(chunk_idx * chunk_size, length(target_levels))
    current_levels <- target_levels[start_idx:end_idx]
    
    # 传入这 6 个品种进行绘制
    draw_variety_plot(subset_data, variety_name, current_levels)
  }
  
  # --- 绘制当前页底部的统一图例 ---
  # 新开一个覆盖整页的透明画板区域，专用于放底部的图例，不破坏原本的 3x2 布局
  par(fig = c(0, 1, 0, 1), oma = c(0, 0, 0, 0), mar = c(0, 0, 0, 0), new = TRUE)
  plot(0, 0, type = "n", bty = "n", xaxt = "n", yaxt = "n", xlab = "", ylab = "")
  
  legend(
    x = "bottom",          # 放置在整个页面正下方
    legend = names(group_colors), 
    fill = group_colors,          
    border = "black", 
    bty = "n", 
    cex = 2, 
    horiz = TRUE, 
    xjust = 0.5, yjust = 0,
    box.lwd = 0,
    inset = c(0, 0.02)     # 离底部边缘微调距离，防遮挡
  )
}

showtext_end()
dev.off()

circos.clear()
cat("PDF导出完成！文件保存至：", pdf_path, "\n")
