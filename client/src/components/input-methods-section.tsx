import { motion } from "framer-motion";
import { Mic, HandMetal, Keyboard } from "lucide-react";

export default function InputMethodsSection() {
  const inputMethods = [
    {
      icon: Mic,
      title: "Voice Commands",
      description: "Natural speech recognition for hands-free interaction with all platform features.",
      color: "primary"
    },
    {
      icon: HandMetal,
      title: "Indian Sign Language",
      description: "Advanced ISL recognition technology for seamless communication and navigation.",
      color: "secondary"
    },
    {
      icon: Keyboard,
      title: "Text & Keyboard",
      description: "Traditional text input with enhanced accessibility features and keyboard shortcuts.",
      color: "accent"
    }
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 50 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6
      }
    }
  };

  return (
    <section className="py-16 bg-muted" id="accessibility" role="region" aria-labelledby="input-methods-heading">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <motion.h2 
          id="input-methods-heading"
          className="text-3xl md:text-4xl font-bold text-center text-foreground mb-12"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          data-testid="input-methods-title"
        >
          Multiple Ways to <span className="text-primary">Interact</span>
        </motion.h2>
        
        <motion.div 
          className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          {inputMethods.map((method, index) => {
            const IconComponent = method.icon;
            return (
              <motion.div 
                key={index}
                className="bg-card text-card-foreground p-8 rounded-xl shadow-lg text-center hover:shadow-xl transition-all duration-300 group"
                variants={itemVariants}
                whileHover={{ y: -8, scale: 1.02 }}
                data-testid={`input-method-${index}`}
              >
                <motion.div 
                  className={`w-16 h-16 bg-${method.color}/10 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-${method.color}/20 transition-colors`}
                  whileHover={{ rotate: 360 }}
                  transition={{ duration: 0.6 }}
                >
                  <IconComponent className={`h-8 w-8 text-${method.color}`} />
                </motion.div>
                <h3 className="text-xl font-semibold mb-3" data-testid={`input-method-title-${index}`}>
                  {method.title}
                </h3>
                <p className="text-muted-foreground" data-testid={`input-method-description-${index}`}>
                  {method.description}
                </p>
              </motion.div>
            );
          })}
        </motion.div>
      </div>
    </section>
  );
}
