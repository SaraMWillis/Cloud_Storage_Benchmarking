# Plotting script for tests done with rclone

library(ggplot2)
library(ggforce)


##### USER OPTIONS #####
# These need to be changed for each individual plot

Title <- "Rclone Speed Test"

Subtitle <- 'HPC to Gdrive, Iterations: 5, Flag: --drive-chunk-size 2G'

Filename <- 'RcloneSpeedTest_HPC_to_GoogleDrive_DriveChunkSizeFlag_Means.csv'

#########################


# Set the working directory so we can save our plots to the correct Plot Output folder
setwd('~/Desktop/ProfilingTest/rclone/Profiling_Output_Figures/')


data_speeds <- read.csv(paste('~/Desktop/ProfilingTest/rclone/Raw_CSV_Output_Files/',Filename,sep=""),header=TRUE)

# Ensures R doesn't force the file sizes to be alphabetized which makes the graphs very questionable
data_speeds$FileSize <-with(data_speeds,factor(FileSize,levels=unique(FileSize)))

# Plots the data points. if/else statements change the formatting of the plot based on the max data point.
ggplot(data_speeds, aes(color='Profiled Speed')) + 
  geom_point(aes(x=FileSize,y=ProfiledSpeed_Mean), size=8,alpha=1)+
  geom_errorbar(aes(x=FileSize,ymin=ProfiledSpeed_Mean-ProfiledSpeed_SE,ymax=ProfiledSpeed_Mean+ProfiledSpeed_SE),width=.05)+
  
  theme(text = element_text(size=25)) +
  theme(legend.justification=c(1,0), legend.position=if(max(data_speeds$ProfiledSpeed_Mean) < 85){c(.95,.05)} else {c(.22,.90)},legend.title= element_blank()) + 
  labs(title=Title,x='File Size',y='Transfer Speed (MB/s)', subtitle = Subtitle)+
  geom_hline(yintercept=max(data_speeds$ProfiledSpeed_Mean)) +
  geom_text(aes(1,max(data_speeds$ProfiledSpeed_Mean),label = signif(max(data_speeds$ProfiledSpeed_Mean),4)), vjust = -0.3, colour='black',size=6)+
  if(max(data_speeds$ProfiledSpeed_Mean) > 85){
    facet_zoom(ylim=c(0,85)) 
  } else {
    ylim(0,85)
  }

# Saves the file as a .png in the working directory specified at the beginning of this script 
ggsave(gsub(".csv",".png",Filename),plot=last_plot(),dpi=300)
