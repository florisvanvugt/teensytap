
fname <- "Alexandra_delaydetection_20171107_130049.txt"
##fname <- 'Robert_delaydetection_20171106_162230.txt'
##fname <- 'Thomas_delaydetection_20171106_151624.txt'
dat <- read.table(fname,header=T)


dat$correct.answer <- ifelse(dat$delay1==0,"second","first")

dat$correct <- dat$correct.answer==dat$response

dat$delay <- dat$delay1+dat$delay2

require('plyr')
summ <- ddply(dat,'delay',summarize,
              n.correct=sum(correct),
              n = length(correct))

summ$prop.correct=summ$n.correct/summ$n
summ

require('ggplot2')

ggplot(summ,
       aes(x=delay,y=prop.correct))+
    geom_point()+
    geom_line()+
    ggtitle(fname)+
    xlab("Delay (ms)")+
    ylab("Proportion correct")
ggsave(paste(fname,".pdf",sep=''))


