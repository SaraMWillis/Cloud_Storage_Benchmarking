library(ggplot2)
library(ggforce)


##### USER OPTIONS #####
# These need to be changed for each individual plot

Title <- "Cyberduck GUI Speed Test"

Subtitle <- 'HPC to Gdrive, Iterations: 5'

Filename <- 'CyberduckGUITest_HPCToGdrive_means.csv'

#########################


# Set the working directory so the output plots are saved to the correct directory
setwd('~/Desktop/ProfilingTest/CyberduckGUI/OutputFigures/')

data_speeds <- read.csv(paste('~/Desktop/ProfilingTest/CyberduckGUI/Raw_CSV_Output_Files/',Filename,sep=""),header=TRUE)
data_speeds$FileSize <-with(data_speeds,factor(FileSize,levels=unique(FileSize)))

head(data_speeds)

reduced_data_frame <- data_speeds[-1,]
reduced_data_frame


ggplot(data_speeds, aes(color='Profiled Speed')) + 
  geom_point(aes(x=FileSize,y=Speed_Mean), size=8,alpha=1)+
  geom_errorbar(aes(x=FileSize,ymin=Speed_Mean-Speed_SE,ymax=Speed_Mean+Speed_SE),width=.05)+
  
  theme(text = element_text(size=25)) +
  theme(legend.justification=c(1,0), legend.position=if(max(reduced_data_frame$Speed_Mean) < 85){c(.95,0.05) } else {c(.22,.90)},legend.title= element_blank()) + 
  labs(title=Title,x='File Size',y='Transfer Speed (MB/s)', subtitle = )+
  geom_hline(yintercept=max(reduced_data_frame$Speed_Mean)) +
  geom_text(aes(1,max(reduced_data_frame$Speed_Mean),label = signif(max(reduced_data_frame$Speed_Mean),4)), vjust = -0.3, colour='black',size=6)+
  if(max(reduced_data_frame$Speed_Mean) > 83){
    facet_zoom(ylim=c(0,85)) 
  } else {
    ylim(0,85)
  }
  facet_zoom(ylim=c(0,85)) 

ggsave(gsub(".csv",".png",Filename),plot=last_plot(),dpi=300)
  