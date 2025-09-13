import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Rocket, Calendar } from "lucide-react";

export default function CTASection() {
  return (
    <section className="py-20" role="region" aria-labelledby="cta-heading">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <motion.h2 
          id="cta-heading"
          className="text-3xl md:text-4xl font-bold text-foreground mb-6"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          data-testid="cta-title"
        >
          Ready to <span className="text-primary">Get Started?</span>
        </motion.h2>
        
        <motion.p 
          className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          viewport={{ once: true }}
          data-testid="cta-description"
        >
          Join thousands of users who have already discovered the freedom and independence that Inlightex provides.
        </motion.p>
        
        <motion.div 
          className="flex flex-col sm:flex-row gap-4 justify-center items-center"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          viewport={{ once: true }}
        >
          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Button 
              size="lg"
              className="bg-primary text-primary-foreground hover:bg-primary/90 px-8 py-4 text-lg font-semibold shadow-lg hover:shadow-xl"
              aria-label="Start your free trial"
              data-testid="button-free-trial"
            >
              <Rocket className="mr-2 h-5 w-5" />
              Start Free Trial
            </Button>
          </motion.div>
          
          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Button 
              variant="outline"
              size="lg"
              className="border-2 border-secondary text-secondary hover:bg-secondary hover:text-secondary-foreground px-8 py-4 text-lg font-semibold"
              aria-label="Schedule a personalized demo"
              data-testid="button-schedule-demo"
            >
              <Calendar className="mr-2 h-5 w-5" />
              Schedule Demo
            </Button>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}
