# Plotting script for tests done with Cyberduck

library(ggforce)
library(ggplot2)

##### USER OPTIONS #####
# These need to be changed for each individual plot

Title <- 'Globus CLI Speed Test'

Subtitle <- 'Personal Computer to AWS S3, Hardline, Iterations: 5'

Filename <- 'GlobusBenchmarkingTest_PersonalComputer_to_AWS_means.csv'

#########################

# Set the working directory so we can save our plots to the correct Plot Output folder
setwd('~/Desktop/ProfilingTest/AWS_S3/GlobusCLI/Profiling_Output_Figures/')


# Reads in our dataframe and forces R to keep the same ordering as the original file. This keeps
# R from attempting to alphabetize the file sizes which leads to weird effects
data_speeds <- read.csv(paste('~/Desktop/ProfilingTest/AWS_S3/GlobusCLI/RawCSVFiles/',Filename,sep=""),header=TRUE)
data_speeds$FileSize <-with(data_speeds,factor(FileSize,levels=unique(FileSize)))

ggplot(data_speeds, aes(color='Globus Estimate')) + 
  geom_point(aes(x=FileSize,y=Speed_Mean), size=8,alpha=1)+
  geom_errorbar(aes(x=FileSize,ymin=Speed_Mean-Speed_SE,ymax=Speed_Mean+Speed_SE),width=.05)+
  
  theme(text = element_text(size=25)) +
  theme(legend.justification=c(1,0), legend.position=c(.22,.90),legend.title= element_blank()) + 
  labs(title=Title,x='File Size',y='Transfer Speed (MB/s)', subtitle = Subtitle)+
  geom_hline(yintercept=max(data_speeds$Speed_Mean)) +
  geom_text(aes(1,max(data_speeds$Speed_Mean),label = signif(max(data_speeds$Speed_Mean),4)), vjust = -0.3, colour='black',size=6)+
  ylim(0,85)

ggsave(gsub(".csv",".png",Filename),plot=last_plot(),dpi=300)
