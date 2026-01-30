import { Link } from 'react-router-dom'

export default function Landing() {
  return (
    <div className="min-h-screen bg-[#1a2e3f] relative overflow-hidden">
      {/* Background Image Overlay */}
      <div
        className="absolute inset-0 bg-cover bg-center opacity-30"
        style={{
          backgroundImage: `url('https://images.unsplash.com/photo-1494412574643-ff11b0a5c1c3?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80')`,
        }}
      />

      {/* Decorative crosses */}
      <div className="absolute top-1/3 left-20 text-gray-600 opacity-30 text-2xl">+</div>
      <div className="absolute top-1/3 right-20 text-gray-600 opacity-30 text-2xl">+</div>
      <div className="absolute bottom-20 left-1/2 text-gray-600 opacity-30 text-2xl">+</div>

      {/* Navigation */}
      <nav className="relative z-10 flex items-center justify-between px-8 py-6">
        {/* Logo */}
        <div className="flex items-center">
          <div className="w-12 h-12 bg-[#1a2e3f] border-2 border-gray-600 flex items-center justify-center">
            <span className="text-white text-2xl font-bold">S</span>
          </div>
          <div className="w-12 h-1 bg-[#c9a227] ml-0"></div>
        </div>

        {/* Nav Links */}
        <div className="hidden md:flex items-center space-x-10">
          <a href="#solution" className="text-gray-300 hover:text-white tracking-widest text-sm font-medium">
            SOLUTION
          </a>
          <a href="#capabilities" className="text-gray-300 hover:text-white tracking-widest text-sm font-medium">
            CAPABILITIES
          </a>
          <a href="#rnd" className="text-[#c9a227] tracking-widest text-sm font-medium">
            SIRA R&D
          </a>
        </div>

        {/* Auth Buttons */}
        <div className="flex items-center space-x-6">
          <Link
            to="/login"
            className="text-gray-300 hover:text-white tracking-widest text-sm font-medium"
          >
            SIGN IN
          </Link>
          <Link
            to="/login"
            className="bg-[#c9a227] hover:bg-[#b8922a] text-white px-6 py-3 tracking-widest text-sm font-medium flex items-center"
          >
            DEMO <span className="ml-2 text-lg">+</span>
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="relative z-10 flex flex-col items-center justify-center min-h-[calc(100vh-100px)] text-center px-4">
        {/* Center Logo */}
        <div className="mb-12">
          <div className="w-24 h-24 bg-white flex items-center justify-center mx-auto">
            <span className="text-[#1a2e3f] text-5xl font-bold">S</span>
          </div>
          <div className="w-16 h-1.5 bg-[#c9a227] mx-auto mt-0"></div>
        </div>

        {/* Main Heading */}
        <h1 className="text-white text-4xl md:text-6xl font-bold tracking-wider mb-6 max-w-4xl leading-tight">
          BUILDING THE FUTURE OF
          <br />
          SUPPLY CHAIN SECURITY
        </h1>

        {/* Subheading */}
        <div className="flex items-center justify-center mb-6">
          <div className="w-16 h-px bg-[#c9a227]"></div>
          <p className="text-gray-400 tracking-widest text-sm mx-4">
            WITH SPEED AND INTELLIGENCE
          </p>
          <div className="w-16 h-px bg-[#c9a227]"></div>
        </div>

        {/* Powered By */}
        <p className="text-[#c9a227] tracking-widest text-sm mb-10">
          POWERED BY ENERGIE PARTNERS
        </p>

        {/* CTA Button */}
        <Link
          to="/login"
          className="bg-[#c9a227] hover:bg-[#b8922a] text-white px-12 py-4 tracking-widest text-sm font-medium transition-colors"
        >
          REQUEST A DEMO
        </Link>
      </main>

      {/* Features Section */}
      <section id="solution" className="relative z-10 py-20 px-8 bg-[#0f1c28]">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-white text-3xl font-bold tracking-wider text-center mb-16">
            OUR SOLUTION
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center p-6">
              <div className="w-16 h-16 bg-[#c9a227] rounded-full flex items-center justify-center mx-auto mb-6">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <h3 className="text-white text-xl font-semibold mb-4">Security Intelligence</h3>
              <p className="text-gray-400">Real-time monitoring and threat detection for your supply chain operations.</p>
            </div>
            <div className="text-center p-6">
              <div className="w-16 h-16 bg-[#c9a227] rounded-full flex items-center justify-center mx-auto mb-6">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-white text-xl font-semibold mb-4">Digital Control Tower</h3>
              <p className="text-gray-400">Centralized visibility into all cargo movements and logistics operations.</p>
            </div>
            <div className="text-center p-6">
              <div className="w-16 h-16 bg-[#c9a227] rounded-full flex items-center justify-center mx-auto mb-6">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-white text-xl font-semibold mb-4">Rapid Response</h3>
              <p className="text-gray-400">Automated alerts and incident response playbooks for quick action.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 py-8 px-8 bg-[#0a141c] text-center">
        <p className="text-gray-500 text-sm">
          &copy; 2024 SIRA Platform. Powered by Energie Partners.
        </p>
      </footer>
    </div>
  )
}
