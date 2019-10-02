# Plotting script for tests done with Cyberduck

library(ggplot2)
library(ggforce)

##### USER OPTIONS #####
# These need to be changed for each individual plot

Title <- 'Cyberduck Speed Test'

Subtitle <- 'Personal Computer to Gdrive, Hardline, Iterations: 5'

Filename <- 'DuckCLI_GoogleDrive_to_HPC_Means.csv'

#########################

# Set the working directory so we can save our plots to the correct Plot Output folder
setwd('~/Desktop/ProfilingTest/CyberduckCLI/Profiling_Output_Figures')


# Reads in our dataframe and forces R to keep the same ordering as the original file. This keeps
# R from attempting to alphabetize the file sizes which leads to weird effects
data_speeds <- read.csv(paste('~/Desktop/ProfilingTest/CyberduckCLI/Raw_CSV_Output_Files/CyberduckCLI/',Filename,sep=""),header=TRUE)
data_speeds$FileSize <-with(data_speeds,factor(FileSize,levels=unique(FileSize)))

# We want to plot both the predicted speeds given by cyberduck itself as well as the speeds predicted
# by our profiler. We split the dataframe into two separate dataframes and then recombine them to 
# allow us to do this
ProfiledSpeeds <- data.frame(data_speeds$ProfiledSpeed_Mean,data_speeds$ProfiledSpeed_SE,data_speeds$FileSize,'Profiled Speed')
names(ProfiledSpeeds) <- c("MeanSpeed",'StandardError','FileSize','Estimator')
cyberduckSpeeds <- data.frame(data_speeds$cyberduckEst_Mean,data_speeds$cyberduckEst_SE,data_speeds$FileSize,'Cyberduck Speed')
names(cyberduckSpeeds) <- c("MeanSpeed",'StandardError','FileSize','Estimator')
CombinedDataFrame <- rbind(ProfiledSpeeds,cyberduckSpeeds)

# ggplot is then used to plot our data
ggplot(CombinedDataFrame,aes(color=Estimator) ) + 
  geom_point(aes(x=FileSize,y=MeanSpeed,colour=factor(Estimator)), size=8,alpha=1)+
  geom_errorbar(aes(x=FileSize,ymin=MeanSpeed-StandardError,ymax=MeanSpeed+StandardError,colour=factor(Estimator)),width=.05)+
  labs(title=Title,x='File Size',y='Transfer Speed (MB/s)', subtitle = Subtitle)+
  theme(text = element_text(size=25)) +
  theme(legend.justification=c(1,0), legend.position=if(max(CombinedDataFrame$MeanSpeed)<85){c(.95,.05)} else {c(.25,.83)}) +
  geom_hline(yintercept=max(data_speeds$ProfiledSpeed_Mean),size=1) + 
  geom_text(aes(1,max(data_speeds$ProfiledSpeed_Mean),label = signif(max(data_speeds$ProfiledSpeed_Mean),4)), vjust = -1, colour='black',size=6) +
  if (max(CombinedDataFrame$MeanSpeed)<85) {
    ylim(0,85)

  }else {
    facet_zoom(ylim=c(0,85))
  }

# The figure then gets saved to the current working directory
ggsave(gsub(".csv",".png",Filename),plot=last_plot(),dpi=300)
