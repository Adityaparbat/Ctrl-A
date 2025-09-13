import { motion } from "framer-motion";
import { 
  AlertTriangle, 
  BookOpen, 
  Share2, 
  Camera, 
  HandHeart, 
  Users 
} from "lucide-react";

export default function FeaturesSection() {
  const features = [
    {
      icon: AlertTriangle,
      title: "Emergency Support",
      description: "Instant emergency assistance with one-touch access to emergency services and designated contacts.",
      bgColor: "bg-red-100",
      hoverBgColor: "group-hover:bg-red-200",
      iconColor: "text-red-600"
    },
    {
      icon: BookOpen,
      title: "Reading Assistant",
      description: "AI-powered text-to-speech and document reading for visually impaired users with customizable voices.",
      bgColor: "bg-blue-100",
      hoverBgColor: "group-hover:bg-blue-200",
      iconColor: "text-blue-600"
    },
    {
      icon: Share2,
      title: "Social Media Posting",
      description: "Simplified social media management with voice commands and accessible posting interfaces.",
      bgColor: "bg-green-100",
      hoverBgColor: "group-hover:bg-green-200",
      iconColor: "text-green-600"
    },
    {
      icon: Camera,
      title: "Camera Navigation",
      description: "Real-time object recognition and navigation assistance for visually impaired individuals.",
      bgColor: "bg-purple-100",
      hoverBgColor: "group-hover:bg-purple-200",
      iconColor: "text-purple-600"
    },
    {
      icon: HandHeart,
      title: "Welfare Schemes Guidance",
      description: "Comprehensive information and application assistance for government welfare programs and benefits.",
      bgColor: "bg-orange-100",
      hoverBgColor: "group-hover:bg-orange-200",
      iconColor: "text-orange-600"
    },
    {
      icon: Users,
      title: "Connecting to Peers",
      description: "Safe community platform to connect with others, share experiences, and build support networks.",
      bgColor: "bg-pink-100",
      hoverBgColor: "group-hover:bg-pink-200",
      iconColor: "text-pink-600"
    }
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
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
    <section className="py-20" id="features" role="region" aria-labelledby="features-heading">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div 
          className="text-center mb-16"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
        >
          <h2 id="features-heading" className="text-3xl md:text-4xl font-bold text-foreground mb-6" data-testid="features-title">
            Comprehensive <span className="text-primary">Support</span> Features
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto" data-testid="features-description">
            Our platform provides essential tools and services designed specifically for the needs of disabled individuals, ensuring safety, independence, and connection.
          </p>
        </motion.div>
        
        <motion.div 
          className="grid md:grid-cols-2 lg:grid-cols-3 gap-8"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          {features.map((feature, index) => {
            const IconComponent = feature.icon;
            return (
              <motion.div 
                key={index}
                className="bg-card text-card-foreground p-6 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 border border-border hover:border-primary/50 group"
                variants={itemVariants}
                whileHover={{ y: -5, scale: 1.02 }}
                data-testid={`feature-${index}`}
              >
                <motion.div 
                  className={`w-12 h-12 ${feature.bgColor} rounded-lg flex items-center justify-center mb-4 ${feature.hoverBgColor} transition-colors`}
                  whileHover={{ rotate: 5 }}
                  transition={{ duration: 0.3 }}
                >
                  <IconComponent className={`h-6 w-6 ${feature.iconColor}`} />
                </motion.div>
                <h3 className="text-xl font-semibold mb-3 text-foreground" data-testid={`feature-title-${index}`}>
                  {feature.title}
                </h3>
                <p className="text-muted-foreground" data-testid={`feature-description-${index}`}>
                  {feature.description}
                </p>
              </motion.div>
            );
          })}
        </motion.div>
      </div>
    </section>
  );
}
