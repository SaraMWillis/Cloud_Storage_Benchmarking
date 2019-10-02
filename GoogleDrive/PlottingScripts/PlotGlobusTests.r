library(ggplot2)
library(ggforce)

##### USER OPTIONS #####

# These need to be changed for each individual plot

Title <- 'Globus Speed Test'

Subtitle <- 'HPC to Gdrive, Iterations: 5'

Filename <- 'GlobusTest_Gdrive_to_PersonalComputer_means.csv'

#########################

# Where the output plot will be saved
setwd('~/Desktop/ProfilingTest/globus/Profiling_Output_Figures/')


data_speeds <- read.csv(paste('~/Desktop/ProfilingTest/globus/Raw_CSV_Files/',Filename,sep=""),header=TRUE)

# Forces the ordering of the dataframe to be unchanged from the original file. If this is not done,
# R will automatically reorder the x-axis to be alphabetized
data_speeds$FileSize <-with(data_speeds,factor(FileSize,levels=unique(FileSize)))

ggplot(data_speeds, aes(color='Globus Estimate')) + 
  geom_point(aes(x=FileSize,y=GlobusSpeedEstimate_Mean), size=8,alpha=1)+
  geom_errorbar(aes(x=FileSize,ymin=GlobusSpeedEstimate_Mean-GlobusSpeedEstimate_SE,ymax=GlobusSpeedEstimate_Mean+GlobusSpeedEstimate_SE),width=.05)+
  
  theme(text = element_text(size=25)) +
  theme(legend.justification=c(1,0), legend.position=c(.95,.05),legend.title= element_blank()) + 
  labs(title=Title,x='File Size',y='Transfer Speed (MB/s)', subtitle = Subtitle)+
  geom_hline(yintercept=max(data_speeds$GlobusSpeedEstimate_Mean)) +
  geom_text(aes(1,max(data_speeds$GlobusSpeedEstimate_Mean),label = signif(max(data_speeds$GlobusSpeedEstimate_Mean),4)), vjust = -0.3, colour='black',size=6)+
  ylim(0,85)

ggsave(gsub(".csv",".png",Filename),plot=last_plot(),dpi=300)
