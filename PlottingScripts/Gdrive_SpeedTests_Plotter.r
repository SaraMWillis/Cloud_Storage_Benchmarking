library(ggplot2)
library(ggforce)


##### USER OPTIONS #####
# These need to be changed for each individual plot

Title <- 'Gdrive Speed Test'

Subtitle <- 'Personal Computer to Google Drive, Hardline, Iterations: 5'

Filename <- 'Gdrive_GoogleDrive_to_HPC_Means.csv'

#########################



# Set the working directory so we can save our plots to the correct Plot Output folder
setwd('~/Desktop/ProfilingTest/Gdrive/Profiling_Output_Figures/')


data_speeds <- read.csv(paste('~/Desktop/ProfilingTest/Gdrive/Profiling_Scripts/',Filename,sep=""),header=TRUE)

# Keeps R from automatically ordering the x-axis, which it will attempt to alphabetize, which messes the whole thing up
data_speeds$FileSize <-with(data_speeds,factor(FileSize,levels=unique(FileSize)))

# Splits the data frame so it can be recombined into format that can be more easily plotted
ProfiledSpeeds <- data.frame(data_speeds$ProfileSpeed_Mean,data_speeds$ProfileSpeed_SE,data_speeds$FileSize,'Profiled Speed')
names(ProfiledSpeeds) <- c("MeanSpeed",'StandardError','FileSize','Estimator')
gdriveSpeeds <- data.frame(data_speeds$GdriveEstimate_Mean,data_speeds$GdriveEstimate_SE,data_speeds$FileSize,'Gdrive Speed')
names(gdriveSpeeds) <- c("MeanSpeed",'StandardError','FileSize','Estimator')

# Binds the smaller dataframes into one large one
CombinedDataFrame <- rbind(ProfiledSpeeds,gdriveSpeeds)

#Changes where the legened is and whether to plot is zoomed or not based on the max data point
ggplot(CombinedDataFrame, aes(color=Estimator)) + 
  geom_point(aes(x=FileSize,y=MeanSpeed), size=8,alpha=1)+
  geom_errorbar(aes(x=FileSize,ymin=MeanSpeed-StandardError,ymax=MeanSpeed+StandardError),width=.05)+
  
  theme(text = element_text(size=25)) +
  theme(legend.justification=c(1,0), legend.position=if(max(CombinedDataFrame$MeanSpeed) < 85){c(.95,0.05) } else {c(.2,.87)},legend.title= element_blank()) + 
  labs(title=Title,x='File Size',y='Transfer Speed (MB/s)', subtitle = Subtitle)+
  geom_hline(yintercept=max(ProfiledSpeeds$MeanSpeed)) +
  geom_text(aes(1,max(CombinedDataFrame$MeanSpeed),label = signif(max(CombinedDataFrame$MeanSpeed),4)), vjust = -0.3, colour='black',size=6)+
  if(max(CombinedDataFrame$MeanSpeed) > 85){
  facet_zoom(ylim=c(0,85)) 
  } else {
  ylim(0,85)#, c(.95,0.05), c(.2,.87)
  }

# Saves the file as a .png in the working directory specified at the beginning of this script
ggsave(gsub(".csv",".png",Filename),plot=last_plot(),dpi=300)
