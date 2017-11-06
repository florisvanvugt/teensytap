

dat <- read.table('robert_delaydetection_20171106_120315.txt',header=T)


dat$correct.answer <- ifelse(dat$delay1==0,"second","first")

dat$correct <- dat$correct.answer==dat$response

dat$delay <- dat$delay1+dat$delay2

require('plyr')
summ <- ddply(dat,'delay',summarize,correct=mean(correct))      


require('ggplot2')

ggplot(summ,
       aes(x=delay,y=correct))+
    geom_bar(stat='identity')
