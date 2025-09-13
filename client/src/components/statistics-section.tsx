import { motion, useInView } from "framer-motion";
import { useEffect, useRef, useState } from "react";

export default function StatisticsSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true });
  
  const stats = [
    { value: 50000, suffix: "+", label: "Active Users" },
    { value: 1000000, suffix: "+", label: "Interactions Daily", format: "1M+" },
    { value: 99.9, suffix: "%", label: "Uptime" },
    { value: 24, suffix: "/7", label: "Support" }
  ];

  const [counters, setCounters] = useState(stats.map(() => 0));

  useEffect(() => {
    if (isInView) {
      stats.forEach((stat, index) => {
        let start = 0;
        const end = stat.value;
        const duration = 2000;
        const increment = end / (duration / 16);
        
        const timer = setInterval(() => {
          start += increment;
          if (start >= end) {
            start = end;
            clearInterval(timer);
          }
          
          setCounters(prev => {
            const newCounters = [...prev];
            newCounters[index] = start;
            return newCounters;
          });
        }, 16);
        
        return () => clearInterval(timer);
      });
    }
  }, [isInView]);

  const formatValue = (value: number, stat: typeof stats[0]) => {
    if (stat.format) return stat.format;
    if (stat.suffix === "%") return `${value.toFixed(1)}%`;
    if (stat.suffix === "/7") return `${Math.floor(value)}/7`;
    return Math.floor(value).toLocaleString() + stat.suffix;
  };

  return (
    <section className="py-16 gradient-bg" role="region" aria-labelledby="stats-heading" ref={ref}>
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <h2 id="stats-heading" className="sr-only">Platform Statistics</h2>
        <motion.div 
          className="grid md:grid-cols-4 gap-8 text-center"
          initial={{ opacity: 0, y: 50 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, staggerChildren: 0.2 }}
        >
          {stats.map((stat, index) => (
            <motion.div 
              key={index}
              className="text-white"
              initial={{ opacity: 0, scale: 0.5 }}
              animate={isInView ? { opacity: 1, scale: 1 } : {}}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              data-testid={`stat-${index}`}
            >
              <motion.div 
                className="text-4xl font-bold mb-2"
                initial={{ scale: 1 }}
                animate={isInView ? { scale: [1, 1.1, 1] } : {}}
                transition={{ duration: 0.6, delay: 0.5 + index * 0.1 }}
                data-testid={`stat-value-${index}`}
              >
                {formatValue(counters[index], stat)}
              </motion.div>
              <div className="text-xl opacity-90" data-testid={`stat-label-${index}`}>
                {stat.label}
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
