import { motion } from "framer-motion";

export default function TestimonialsSection() {
  const testimonials = [
    {
      name: "Sarah M.",
      condition: "Visual Impairment",
      image: "https://images.unsplash.com/photo-1582750433449-648ed127bb54?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=150&h=150",
      quote: "The camera navigation feature has revolutionized how I move around the city. I feel more confident and independent than ever before."
    },
    {
      name: "Michael R.",
      condition: "Mobility Impairment",
      image: "https://images.unsplash.com/photo-1607990281513-2c110a25bd8c?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=150&h=150",
      quote: "The emergency support system gave my family peace of mind. I can live independently knowing help is always just a voice command away."
    },
    {
      name: "Priya K.",
      condition: "Hearing Impairment",
      image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=150&h=150",
      quote: "Finally, a platform that truly understands ISL! The sign language recognition is incredibly accurate and makes communication effortless."
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
    hidden: { opacity: 0, y: 30 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6
      }
    }
  };

  return (
    <section className="py-20 bg-muted" role="region" aria-labelledby="testimonials-heading">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <motion.h2 
          id="testimonials-heading"
          className="text-3xl md:text-4xl font-bold text-center text-foreground mb-16"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          data-testid="testimonials-title"
        >
          What Our <span className="text-primary">Community</span> Says
        </motion.h2>
        
        <motion.div 
          className="grid md:grid-cols-2 lg:grid-cols-3 gap-8"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          {testimonials.map((testimonial, index) => (
            <motion.div 
              key={index}
              className="bg-card text-card-foreground p-6 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300"
              variants={itemVariants}
              whileHover={{ y: -5, scale: 1.02 }}
              data-testid={`testimonial-${index}`}
            >
              <div className="flex items-center mb-4">
                <motion.img 
                  src={testimonial.image}
                  alt={`Portrait of ${testimonial.name}, a satisfied Inlightex user`}
                  className="w-12 h-12 rounded-full mr-4 object-cover"
                  whileHover={{ scale: 1.1 }}
                  transition={{ duration: 0.3 }}
                  data-testid={`testimonial-image-${index}`}
                />
                <div>
                  <h4 className="font-semibold" data-testid={`testimonial-name-${index}`}>
                    {testimonial.name}
                  </h4>
                  <p className="text-sm text-muted-foreground" data-testid={`testimonial-condition-${index}`}>
                    {testimonial.condition}
                  </p>
                </div>
              </div>
              <p className="text-muted-foreground italic" data-testid={`testimonial-quote-${index}`}>
                "{testimonial.quote}"
              </p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
