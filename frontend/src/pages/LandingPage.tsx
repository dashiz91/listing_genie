import React from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
  CheckCircle2,
  CloudUpload,
  Edit3,
  History,
  ImagePlus,
  Monitor,
  Palette,
  RefreshCw,
  Send,
  Smartphone,
  Sparkles,
  UserRound,
  WandSparkles,
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

type Step = {
  title: string;
  description: string;
  icon: React.ReactNode;
};

type Plan = {
  name: string;
  price: string;
  credits: string;
  bestFor: string;
  highlights: string[];
  featured?: boolean;
};

type ShowcaseOutput = {
  title: string;
  src: string;
};

type CaseStudy = {
  id: number;
  code: string;
  title: string;
  subtitle: string;
  status: 'live' | 'placeholder';
  beforeSrc?: string;
  heroSrc?: string;
  listingOutputs?: ShowcaseOutput[];
  aplusDesktopOutputs?: ShowcaseOutput[];
  aplusMobileOutputs?: ShowcaseOutput[];
};

const steps: Step[] = [
  {
    title: 'Upload Product Photos',
    description:
      'Start with rough phone photos. The workflow is built for real seller inputs, not perfect studio shots.',
    icon: <ImagePlus className="h-5 w-5" />,
  },
  {
    title: 'Generate Listing Pack',
    description:
      'Generate a complete set: hero, infographics, lifestyle, and comparison assets in one run.',
    icon: <WandSparkles className="h-5 w-5" />,
  },
  {
    title: 'Build A+ Content',
    description:
      'Turn the same product story into desktop and mobile A+ modules ready for publishing.',
    icon: <Monitor className="h-5 w-5" />,
  },
  {
    title: 'Ship Faster',
    description: 'Review, export, and publish with less iteration friction and stronger listing consistency.',
    icon: <Smartphone className="h-5 w-5" />,
  },
];

const caseStudies: CaseStudy[] = [
  {
    id: 1,
    code: '01',
    title: 'Moon Face Planter',
    subtitle: 'Nebula Colors - from amateur photo to full listing + A+ stack',
    status: 'live',
    beforeSrc: '/images/landing/showcase/moon-before-amateur.png',
    heroSrc: '/images/landing/showcase/moon-hero-white.png',
    listingOutputs: [
      { title: 'Main Image', src: '/images/landing/showcase/moon-hero-white.png' },
      { title: 'Infographic 1', src: '/images/landing/showcase/moon-infographic-1.png' },
      { title: 'Infographic 2', src: '/images/landing/showcase/moon-infographic-2.png' },
      { title: 'Lifestyle', src: '/images/landing/showcase/moon-lifestyle.png' },
      { title: 'Comparison', src: '/images/landing/showcase/moon-comparison.png' },
    ],
    aplusDesktopOutputs: [
      { title: 'A+ Desktop Stack', src: '/images/landing/showcase/moon-aplus-desktop.png' },
    ],
    aplusMobileOutputs: [
      { title: 'A+ Mobile Stack', src: '/images/landing/showcase/moon-aplus-mobile.png' },
    ],
  },
  {
    id: 2,
    code: '02',
    title: 'JollyDrop Swedish Candy Mix',
    subtitle: 'Live project: full listing + A+ desktop + A+ mobile outputs from one product input',
    status: 'live',
    beforeSrc: '/images/landing/showcase/session-4657/before-input.png',
    heroSrc: '/images/landing/showcase/session-4657/listing-main.png',
    listingOutputs: [
      { title: 'Main Image', src: '/images/landing/showcase/session-4657/listing-main.png' },
      { title: 'Infographic 1', src: '/images/landing/showcase/session-4657/listing-infographic_1.png' },
      { title: 'Infographic 2', src: '/images/landing/showcase/session-4657/listing-infographic_2.png' },
      { title: 'Lifestyle', src: '/images/landing/showcase/session-4657/listing-lifestyle.png' },
      { title: 'Transformation', src: '/images/landing/showcase/session-4657/listing-transformation.png' },
      { title: 'Comparison', src: '/images/landing/showcase/session-4657/listing-comparison.png' },
    ],
    aplusDesktopOutputs: [
      { title: 'Module 1', src: '/images/landing/showcase/session-4657/aplus-desktop-0.png' },
      { title: 'Module 2', src: '/images/landing/showcase/session-4657/aplus-desktop-1.png' },
      { title: 'Module 3', src: '/images/landing/showcase/session-4657/aplus-desktop-2.png' },
      { title: 'Module 4', src: '/images/landing/showcase/session-4657/aplus-desktop-3.png' },
      { title: 'Module 5', src: '/images/landing/showcase/session-4657/aplus-desktop-4.png' },
      { title: 'Module 6', src: '/images/landing/showcase/session-4657/aplus-desktop-5.png' },
    ],
    aplusMobileOutputs: [
      { title: 'Hero Mobile', src: '/images/landing/showcase/session-4657/aplus-mobile-0.png' },
      { title: 'Module 3 Mobile', src: '/images/landing/showcase/session-4657/aplus-mobile-2.png' },
      { title: 'Module 4 Mobile', src: '/images/landing/showcase/session-4657/aplus-mobile-3.png' },
      { title: 'Module 5 Mobile', src: '/images/landing/showcase/session-4657/aplus-mobile-4.png' },
      { title: 'Module 6 Mobile', src: '/images/landing/showcase/session-4657/aplus-mobile-5.png' },
    ],
  },
  {
    id: 3,
    code: '03',
    title: 'Next Brand Example',
    subtitle: 'Placeholder - adding third real customer case soon',
    status: 'placeholder',
  },
];

const capabilityCards = [
  {
    title: 'Fully Versioned Outputs',
    description: 'Track and compare every iteration so your team can roll back or reuse winning versions.',
    icon: <History className="h-5 w-5" />,
  },
  {
    title: 'Fine-Grain Regenerations',
    description: 'Regenerate specific modules without redoing the entire listing set.',
    icon: <RefreshCw className="h-5 w-5" />,
  },
  {
    title: 'Direct Edits',
    description: 'Adjust content quickly with focused edit controls at image/module level.',
    icon: <Edit3 className="h-5 w-5" />,
  },
  {
    title: 'Style Upload + Selection',
    description: 'Upload references or choose styles so generated visuals stay brand-consistent.',
    icon: <Palette className="h-5 w-5" />,
  },
  {
    title: 'AI Suggests Direction',
    description: 'Let the AI propose visual concepts when you do not have a clear art direction yet.',
    icon: <Sparkles className="h-5 w-5" />,
  },
  {
    title: 'Push Directly to Amazon',
    description: 'Move approved images from project workflow toward Amazon publishing faster.',
    icon: <Send className="h-5 w-5" />,
  },
];

const plans: Plan[] = [
  {
    name: 'Starter',
    price: '$9.99',
    credits: '25 credits',
    bestFor: 'Testing your first products',
    highlights: ['All image types', 'Style library access', 'Project history'],
  },
  {
    name: 'Pro',
    price: '$29.99',
    credits: '100 credits',
    bestFor: 'Growing brands shipping weekly',
    highlights: ['Priority generation', 'A+ workflow support', 'Advanced variations'],
    featured: true,
  },
  {
    name: 'Agency',
    price: '$99.99',
    credits: '500 credits',
    bestFor: 'Teams running multiple catalogs',
    highlights: ['High-volume throughput', 'Faster queue times', 'Account-level scale'],
  },
];

const faqs = [
  {
    q: 'Do I need perfect product photos before uploading?',
    a: 'No. Clean smartphone or simple product shots are usually enough to start. You can refine style and composition after generation.',
  },
  {
    q: 'How many outputs do I get from one workflow?',
    a: 'Each completed run is built around a full listing image set so you can move faster without assembling visuals one by one.',
  },
  {
    q: 'Can I iterate after generation?',
    a: 'Yes. The editor flow is made for edits, regenerate actions, and versioning until your listing looks right.',
  },
];

export const LandingPage: React.FC = () => {
  const { user } = useAuth();
  const [activeCaseId, setActiveCaseId] = React.useState(1);
  const activeCase = caseStudies.find((item) => item.id === activeCaseId) ?? caseStudies[0];
  const isLiveCase = activeCase.status === 'live';
  const placeholderListingNames = ['Main Image', 'Infographic 1', 'Infographic 2', 'Lifestyle', 'Transformation', 'Comparison'];
  const activeListingOutputs = isLiveCase
    ? activeCase.listingOutputs ?? []
    : placeholderListingNames.map((name) => ({ title: name, src: '' }));
  const activeAplusDesktopOutputs = isLiveCase ? activeCase.aplusDesktopOutputs ?? [] : [];
  const activeAplusMobileOutputs = isLiveCase ? activeCase.aplusMobileOutputs ?? [] : [];

  return (
    <div className="landing-premium min-h-screen">
      <div className="landing-ambient" aria-hidden />

      <header className="landing-nav">
        <div className="mx-auto flex w-full max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <Link to="/" className="inline-flex items-center gap-3">
            <div className="landing-logo-shell">
              <img src="/logo/fox-icon-tight.png" alt="reddstudio.ai logo" className="landing-fox-logo" />
            </div>
            <div className="leading-none">
              <div className="landing-brand-title">reddstudio.ai</div>
              <div className="landing-brand-subtitle">AI ecommerce creative platform</div>
            </div>
          </Link>

          <nav className="hidden items-center gap-8 text-sm text-slate-300 md:flex">
            <a href="#before-after" className="landing-link">
              Before / After
            </a>
            <a href="#listing-pack" className="landing-link">
              Listing Pack
            </a>
            <a href="#aplus" className="landing-link">
              A+ Content
            </a>
            <a href="#pricing" className="landing-link">
              Pricing
            </a>
            <a href="#faq" className="landing-link">
              FAQ
            </a>
          </nav>

          <div className="flex items-center gap-3">
            <Link to={user ? '/app' : '/login'} className="landing-btn landing-btn-ghost">
              {user ? 'Open App' : 'Sign In'}
            </Link>
            <Link to={user ? '/app' : '/login'} className="landing-btn landing-btn-solid">
              {user ? 'Go to Workspace' : 'Start Free'}
            </Link>
          </div>
        </div>
      </header>

      <main>
        <section className="relative overflow-hidden px-4 pb-16 pt-16 sm:px-6 sm:pt-20 lg:px-8 lg:pb-24">
          <div className="mx-auto grid w-full max-w-7xl items-center gap-10 lg:grid-cols-12">
            <div className="landing-reveal lg:col-span-5">
              <div className="landing-pill mb-6">
                <Sparkles className="h-4 w-4" />
                Built for real sellers, by real sellers
              </div>
              <h1 className="landing-heading text-4xl leading-tight text-white sm:text-5xl xl:text-6xl">
                Turn rough product photos into conversion-ready Amazon visuals.
              </h1>
              <p className="mt-6 max-w-xl text-lg text-slate-300 sm:text-xl">
                One workflow for the full story: amateur input photo, polished listing images, and complete A+ modules for desktop
                and mobile.
              </p>
              <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                <Link to={user ? '/app' : '/login'} className="landing-btn landing-btn-solid justify-center sm:justify-start">
                  Start Free
                  <ArrowRight className="h-4 w-4" />
                </Link>
                <a href="#before-after" className="landing-btn landing-btn-ghost justify-center sm:justify-start">
                  See Real Example
                </a>
              </div>
            </div>

            <div className="landing-reveal lg:col-span-7" style={{ animationDelay: '0.15s' }}>
              <div className="landing-screen-wrap">
                <div className="landing-screen-topbar">
                  <span />
                  <span />
                  <span />
                </div>
                <img
                  src={isLiveCase ? activeCase.heroSrc : '/images/landing/showcase/session-4657/listing-main.png'}
                  alt="Clean hero image generated for Amazon listing"
                  className="landing-screen-image"
                />
                <div className="landing-screen-fade" />
              </div>
              <div className="mt-4 grid gap-3 sm:grid-cols-3">
                <div className="landing-mini-stat landing-reveal" style={{ animationDelay: '0.2s' }}>
                  <div className="landing-mini-stat-value">1 input</div>
                  <div className="landing-mini-stat-label">Use the original product shot</div>
                </div>
                <div className="landing-mini-stat landing-reveal" style={{ animationDelay: '0.28s' }}>
                  <div className="landing-mini-stat-value">{activeListingOutputs.length} listing images</div>
                  <div className="landing-mini-stat-label">Main + infographics + lifestyle + transformation + comparison</div>
                </div>
                <div className="landing-mini-stat landing-reveal" style={{ animationDelay: '0.36s' }}>
                  <div className="landing-mini-stat-value">A+ ready</div>
                  <div className="landing-mini-stat-label">
                    {activeAplusDesktopOutputs.length} desktop and {activeAplusMobileOutputs.length} mobile modules
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="before-after" className="px-4 py-14 sm:px-6 lg:px-8 lg:py-20">
          <div className="mx-auto w-full max-w-7xl">
            <div className="landing-section-header">
              <p className="landing-kicker">Before / After</p>
              <h2 className="landing-heading text-3xl text-white sm:text-4xl">Show the transformation in seconds</h2>
              <p className="mx-auto mt-4 max-w-3xl text-slate-300">
                Lead with the problem your customers already have: raw, amateur photography. Then reveal the finished listing
                outputs and A+ assets as one cohesive upgrade.
              </p>
            </div>

            <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
              {caseStudies.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setActiveCaseId(item.id)}
                  className={`landing-case-pill ${activeCaseId === item.id ? 'landing-case-pill-active' : ''}`}
                >
                  <span>{item.code}</span>
                  <small>{item.status === 'live' ? 'Live Example' : 'Placeholder'}</small>
                </button>
              ))}
            </div>
            <p className="mt-3 text-center text-sm text-slate-400">
              {activeCase.title}: {activeCase.subtitle}
            </p>

            <div className="mt-12 grid gap-6 lg:grid-cols-12">
              <article className="landing-card overflow-hidden lg:col-span-5">
                <div className="landing-card-label">Input Photo (Amateur)</div>
                {isLiveCase ? (
                  <div className="h-[30rem] bg-slate-950/55 p-3 sm:h-[34rem]">
                    <img
                      src={activeCase.beforeSrc}
                      alt="Amateur product photo before optimization"
                      className="h-full w-full object-contain"
                      loading="lazy"
                    />
                  </div>
                ) : (
                  <div className="landing-placeholder-panel h-96">
                    <CloudUpload className="h-6 w-6" />
                    <p>Case {activeCase.code} placeholder</p>
                    <span>Raw input example will appear here.</span>
                  </div>
                )}
                <div className="p-4 text-sm text-slate-300">
                  Blurry, low-context product input becomes your conversion story starting point.
                </div>
              </article>

              <article className="landing-card overflow-hidden lg:col-span-7">
                <div className="landing-card-label">Output Hero (Amazon Ready)</div>
                {isLiveCase ? (
                  <div className="h-[30rem] bg-slate-950/55 p-3 sm:h-[34rem]">
                    <img
                      src={activeCase.heroSrc}
                      alt="Clean hero image generated on white background"
                      className="h-full w-full object-contain"
                      loading="lazy"
                    />
                  </div>
                ) : (
                  <div className="landing-placeholder-panel h-96">
                    <Sparkles className="h-6 w-6" />
                    <p>Case {activeCase.code} placeholder</p>
                    <span>Generated hero output will appear here.</span>
                  </div>
                )}
                <div className="p-4 text-sm text-slate-300">
                  Clean hero composition built for high-conversion product presentation.
                </div>
              </article>
            </div>
          </div>
        </section>

        <section id="workflow" className="px-4 py-14 sm:px-6 lg:px-8 lg:py-20">
          <div className="mx-auto w-full max-w-7xl">
            <div className="landing-section-header">
              <p className="landing-kicker">Workflow</p>
              <h2 className="landing-heading text-3xl text-white sm:text-4xl">One system for the full listing narrative</h2>
            </div>
            <div className="mt-10 landing-card p-6 sm:p-8">
              <div className="grid gap-6 md:grid-cols-2">
                {steps.map((step, index) => (
                  <div key={step.title} className="flex items-start gap-4">
                    <div className="landing-step-icon">
                      {step.icon}
                      <span>{index + 1}</span>
                    </div>
                    <div>
                      <h3 className="landing-heading text-lg text-white">{step.title}</h3>
                      <p className="mt-1 text-sm leading-relaxed text-slate-300">{step.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section id="capabilities" className="px-4 py-14 sm:px-6 lg:px-8 lg:py-20">
          <div className="mx-auto w-full max-w-7xl">
            <div className="landing-section-header">
              <p className="landing-kicker">Capabilities</p>
              <h2 className="landing-heading text-3xl text-white sm:text-4xl">Built for production, not just one-click demos</h2>
              <p className="mx-auto mt-4 max-w-3xl text-slate-300">
                The platform is designed for operators who need repeatable output quality at scale.
              </p>
            </div>
            <div className="mt-12 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {capabilityCards.map((item) => (
                <article key={item.title} className="landing-card p-5">
                  <div className="mb-3 inline-flex h-9 w-9 items-center justify-center rounded-lg border border-redd-400/50 bg-redd-500/10 text-redd-300">
                    {item.icon}
                  </div>
                  <h3 className="landing-heading text-lg text-white">{item.title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-slate-300">{item.description}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section id="listing-pack" className="px-4 py-14 sm:px-6 lg:px-8 lg:py-20">
          <div className="mx-auto w-full max-w-7xl">
            <div className="landing-section-header">
              <p className="landing-kicker">Listing Pack</p>
              <h2 className="landing-heading text-3xl text-white sm:text-4xl">All core listing assets from one source input</h2>
              <p className="mx-auto mt-4 max-w-3xl text-slate-300">
                Instead of producing assets one-by-one, generate a complete listing set with consistent product identity.
              </p>
            </div>
            <p className="mt-4 text-center text-sm text-slate-400">Scroll the widget row and scroll inside each card to inspect details.</p>
            <div className="landing-scroll-x mt-10 flex gap-4 overflow-x-auto pb-2">
              {activeListingOutputs.map((item) => (
                <article key={item.title} className="landing-card w-[17.25rem] shrink-0 overflow-hidden">
                  <div className="landing-scroll-frame landing-scroll-hint-frame h-64 w-full overflow-y-auto bg-slate-950/45 p-2">
                    {isLiveCase ? (
                      <img src={item.src} alt={item.title} className="block w-full h-auto" loading="lazy" />
                    ) : (
                      <div className="landing-placeholder-panel h-full">
                        <Sparkles className="h-5 w-5" />
                        <p>{item.title}</p>
                        <span>Coming soon</span>
                      </div>
                    )}
                  </div>
                  <div className="p-3 text-center">
                    <h3 className="landing-heading text-sm text-white">{item.title}</h3>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section id="aplus" className="px-4 py-14 sm:px-6 lg:px-8 lg:py-20">
          <div className="mx-auto w-full max-w-7xl">
            <div className="landing-section-header">
              <p className="landing-kicker">A+ Content</p>
              <h2 className="landing-heading text-3xl text-white sm:text-4xl">Desktop and mobile modules from the same product story</h2>
            </div>
            <p className="mt-4 text-center text-sm text-slate-400">Both previews are scrollable. Pull down inside each panel to explore the full stack.</p>
            <div className="mt-12 grid gap-6 lg:grid-cols-12">
              <article className="landing-card overflow-hidden lg:col-span-8">
                <div className="landing-card-label">A+ Desktop</div>
                <div className="landing-scroll-frame landing-scroll-hint-frame h-[44rem] overflow-y-auto lg:h-[48rem]">
                  {isLiveCase && activeAplusDesktopOutputs.length > 0 ? (
                    <div className="space-y-3 bg-slate-950/55 p-3">
                      {activeAplusDesktopOutputs.map((item) => (
                        <figure key={item.title} className="overflow-hidden rounded-xl border border-slate-700/80 bg-slate-950/70">
                          <img src={item.src} alt={item.title} className="block w-full h-auto" loading="lazy" />
                          <figcaption className="px-3 py-2 text-xs font-medium tracking-wide text-slate-300">{item.title}</figcaption>
                        </figure>
                      ))}
                    </div>
                  ) : (
                    <div className="landing-placeholder-panel h-full">
                      <Monitor className="h-6 w-6" />
                      <p>A+ Desktop Placeholder</p>
                      <span>Example {activeCase.code} will be added here.</span>
                    </div>
                  )}
                </div>
              </article>
              <article className="landing-card overflow-hidden lg:col-span-4">
                <div className="landing-card-label">A+ Mobile</div>
                <div className="landing-scroll-frame landing-scroll-hint-frame h-[44rem] overflow-y-auto lg:h-[48rem]">
                  {isLiveCase && activeAplusMobileOutputs.length > 0 ? (
                    <div className="space-y-3 bg-slate-950/55 p-3">
                      {activeAplusMobileOutputs.map((item) => (
                        <figure key={item.title} className="overflow-hidden rounded-xl border border-slate-700/80 bg-slate-950/70">
                          <img src={item.src} alt={item.title} className="block w-full h-auto" loading="lazy" />
                          <figcaption className="px-3 py-2 text-xs font-medium tracking-wide text-slate-300">{item.title}</figcaption>
                        </figure>
                      ))}
                    </div>
                  ) : (
                    <div className="landing-placeholder-panel h-full">
                      <Smartphone className="h-6 w-6" />
                      <p>A+ Mobile Placeholder</p>
                      <span>Example {activeCase.code} will be added here.</span>
                    </div>
                  )}
                </div>
              </article>
            </div>
          </div>
        </section>

        <section id="about-founder" className="px-4 py-14 sm:px-6 lg:px-8 lg:py-20">
          <div className="mx-auto w-full max-w-6xl">
            <article className="landing-card p-6 sm:p-8 lg:p-10">
              <div className="mb-4 inline-flex h-10 w-10 items-center justify-center rounded-xl border border-redd-400/50 bg-redd-500/10 text-redd-300">
                <UserRound className="h-5 w-5" />
              </div>
              <p className="landing-kicker">Founder Story</p>
              <h2 className="landing-heading mt-2 text-3xl text-white sm:text-4xl">Built first for Nebula Colors, now opened to other sellers</h2>
              <p className="mt-4 max-w-4xl text-slate-300">
                I built this workflow to keep my own brand, Nebula Colors, alive while running a full-time data engineering career.
                The result is a system focused on real marketplace execution, not generic image generation demos.
              </p>
              <p className="mt-3 max-w-4xl text-slate-300">
                Everything here comes from actual seller pain: version chaos, slow revisions, inconsistent style, and publishing
                bottlenecks. That is why reddstudio.ai is built around full listing + A+ delivery and direct Amazon-ready operations.
              </p>
            </article>
          </div>
        </section>

        <section id="pricing" className="px-4 py-14 sm:px-6 lg:px-8 lg:py-20">
          <div className="mx-auto w-full max-w-7xl">
            <div className="landing-section-header">
              <p className="landing-kicker">Pricing</p>
              <h2 className="landing-heading text-3xl text-white sm:text-4xl">Simple credit model, no lock-in</h2>
              <p className="mx-auto mt-4 max-w-3xl text-slate-300">
                Choose the volume that fits your current pace. Upgrade as your listing output increases.
              </p>
            </div>

            <div className="mt-12 grid gap-6 md:grid-cols-3">
              {plans.map((plan) => (
                <article
                  key={plan.name}
                  className={`landing-card p-6 ${plan.featured ? 'ring-1 ring-redd-400/70 shadow-[0_0_0_1px_rgba(200,90,53,0.35),0_24px_60px_rgba(200,90,53,0.18)]' : ''}`}
                >
                  {plan.featured ? <div className="landing-plan-badge">Most Selected</div> : null}
                  <h3 className="landing-heading text-2xl text-white">{plan.name}</h3>
                  <p className="mt-2 text-sm text-slate-300">{plan.bestFor}</p>
                  <div className="mt-6 flex items-end gap-2">
                    <span className="landing-heading text-4xl text-white">{plan.price}</span>
                    <span className="pb-1 text-sm text-slate-400">one-time</span>
                  </div>
                  <p className="mt-1 text-sm font-medium text-redd-300">{plan.credits}</p>

                  <ul className="mt-6 space-y-2">
                    {plan.highlights.map((item) => (
                      <li key={item} className="flex items-center gap-2 text-sm text-slate-200">
                        <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                        {item}
                      </li>
                    ))}
                  </ul>

                  <Link
                    to={user ? '/app' : '/login'}
                    className={`mt-7 inline-flex w-full items-center justify-center gap-2 rounded-xl px-4 py-3 text-sm font-semibold transition ${
                      plan.featured
                        ? 'bg-redd-500 text-white hover:bg-redd-400'
                        : 'border border-slate-600 bg-slate-800/90 text-slate-100 hover:border-slate-500 hover:bg-slate-700/90'
                    }`}
                  >
                    {user ? 'Open Workspace' : 'Start with ' + plan.name}
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section id="faq" className="px-4 pb-20 pt-14 sm:px-6 lg:px-8 lg:pb-24 lg:pt-20">
          <div className="mx-auto w-full max-w-5xl">
            <div className="landing-section-header">
              <p className="landing-kicker">FAQ</p>
              <h2 className="landing-heading text-3xl text-white sm:text-4xl">Answers before you get started</h2>
            </div>

            <div className="mt-10 space-y-4">
              {faqs.map((faq) => (
                <details key={faq.q} className="landing-card group p-5">
                  <summary className="landing-heading cursor-pointer list-none pr-8 text-lg text-white marker:hidden">
                    {faq.q}
                  </summary>
                  <p className="mt-3 text-sm leading-relaxed text-slate-300">{faq.a}</p>
                </details>
              ))}
            </div>
          </div>
        </section>

        <section className="px-4 pb-20 sm:px-6 lg:px-8 lg:pb-24">
          <div className="mx-auto flex w-full max-w-6xl flex-col items-center rounded-3xl border border-redd-500/30 bg-gradient-to-br from-slate-900/95 via-slate-900/85 to-redd-950/35 p-10 text-center shadow-[0_30px_90px_rgba(0,0,0,0.45)] sm:p-14">
            <p className="landing-kicker">Ready to Ship Better Listings</p>
            <h2 className="landing-heading mt-2 max-w-3xl text-3xl text-white sm:text-4xl">
              Show customers exactly how one rough photo becomes a complete Amazon-ready listing.
            </h2>
            <p className="mt-4 max-w-2xl text-slate-300">
              This is the visual proof section most landing pages skip. Use it to close faster.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Link to={user ? '/app' : '/login'} className="landing-btn landing-btn-solid">
                {user ? 'Go to Workspace' : 'Start Free'}
                <ArrowRight className="h-4 w-4" />
              </Link>
              <a href="#before-after" className="landing-btn landing-btn-ghost">
                Review Before / After
              </a>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
};
