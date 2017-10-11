


## These data were collected by having no pressure on the FSR
## Sampling period is 50 ms (i.e. 20 Hz)
fileName <- "test_nopressure_20171011_120822.txt"
readings.str <- readChar(fileName, file.info(fileName)$size)

readings <- data.frame(reading=as.numeric(strsplit(readings.str,"\n")[[1]]))
readings <- subset(readings,!is.na(reading))

require('ggplot2')
theme_set(theme_classic())

table(readings$reading)


require('MASS')

x <- readings$reading

res <- fitdistr(x, "gamma")

shape <- res$estimate[["shape"]]
rate  <- res$estimate[["rate"]]



maxx <- 10
xs <- seq(0,maxx,length.out=100)



ggplot()+
    geom_bar(aes(x=readings$reading),
             colour="black")+
    geom_line(aes(x=xs,y=nrow(readings)*dgamma(xs,shape,rate)), color="red", size = 1)+
    scale_x_continuous(breaks=1:maxx)
    



ggplot()+
    geom_line(aes(x=xs,y=1-pgamma(xs,shape,rate)), color="red", size = 1)+
    scale_x_continuous(breaks=1:maxx)+
    scale_y_log10()


## How many false alarms (taps that are not really taps) can we expect
## based on a particular cutoff setting?
cutoff <- 1:20
fa <- data.frame(cutoff=cutoff,
                 p.cr  = pgamma(cutoff,shape,rate))
fa$p.fa <- 1-fa$p.cr

fa$one.in <- 1/fa$p.fa

## If we sample at 1kHz and we let it run for 1 hour, what is the
## chance of getting a false positive?
n.samples <- 1000*60*60

fa$p.FA.in.sample <- 1-((fa$p.cr)**n.samples)

