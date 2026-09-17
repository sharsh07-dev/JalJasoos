"use client";
import React from "react";
import { useAuth } from "@/contexts/AuthContext";
import { Droplet, Shield, Building, Wrench, Home, ChevronRight } from "lucide-react";

export default function LoginPage() {
  const { login } = useAuth();

  const roles = [
    { 
      id: "SUPER_ADMIN", 
      title: "Super Admin", 
      desc: "Global overview & network control", 
      icon: Shield, 
      color: "text-[#8A2BE2]", 
      bg: "bg-[#8A2BE2]/10",
      hoverBorder: "group-hover:border-[#8A2BE2]/30"
    },
    { 
      id: "FACILITY_MANAGER", 
      title: "Facility Manager", 
      desc: "Manage specific society operations", 
      icon: Building, 
      color: "text-[#0071E3]", 
      bg: "bg-[#0071E3]/10",
      hoverBorder: "group-hover:border-[#0071E3]/30"
    },
    { 
      id: "MAINTENANCE_STAFF", 
      title: "Maintenance Staff", 
      desc: "Handle alerts & repair work orders", 
      icon: Wrench, 
      color: "text-[#FF9500]", 
      bg: "bg-[#FF9500]/10",
      hoverBorder: "group-hover:border-[#FF9500]/30"
    },
    { 
      id: "RESIDENT", 
      title: "Resident", 
      desc: "View personal household consumption", 
      icon: Home, 
      color: "text-[#34C759]", 
      bg: "bg-[#34C759]/10",
      hoverBorder: "group-hover:border-[#34C759]/30"
    }
  ];

  return (
    <div className="relative min-h-screen bg-[#F5F5F7] flex flex-col justify-center items-center p-4 font-sans selection:bg-[#0071E3] selection:text-white overflow-hidden">
      
      {/* Background Ambient Orbs */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-[#0071E3] opacity-[0.04] blur-[120px]"></div>
        <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-[#34C759] opacity-[0.04] blur-[120px]"></div>
      </div>

      <div className="relative z-10 w-full max-w-[460px]">
        
        {/* Header / Logo */}
        <div className="flex flex-col items-center mb-10">
          <div className="relative w-20 h-20 bg-white rounded-[22px] shadow-[0_8px_30px_rgb(0,0,0,0.06)] flex items-center justify-center mb-6 overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-[#0071E3]/10 to-transparent"></div>
            <Droplet className="text-[#0071E3] relative z-10" strokeWidth={1.5} size={36} />
          </div>
          <h1 className="text-[32px] font-semibold tracking-tight text-[#1D1D1F] mb-2">
            JalJasoos
          </h1>
          <p className="text-[16px] text-[#86868B] text-center px-4">
            Select your role to enter the interactive environment.
          </p>
        </div>

        {/* Role Selector Card */}
        <div className="bg-white/80 backdrop-blur-xl rounded-[28px] shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-white p-3 space-y-2">
          {roles.map((r) => {
            const Icon = r.icon;
            return (
              <button
                key={r.id}
                onClick={() => login(r.id)}
                className={`w-full flex items-center gap-4 px-4 py-4 rounded-[20px] bg-transparent hover:bg-white transition-all duration-300 text-left group border border-transparent ${r.hoverBorder} hover:shadow-[0_4px_20px_rgb(0,0,0,0.03)]`}
              >
                {/* Icon Container */}
                <div className={`w-12 h-12 rounded-[16px] flex items-center justify-center shrink-0 ${r.bg} transition-transform duration-300 group-hover:scale-105`}>
                  <Icon className={r.color} size={22} strokeWidth={2} />
                </div>
                
                {/* Text Content */}
                <div className="flex-1">
                  <span className="block text-[17px] font-semibold text-[#1D1D1F] transition-colors">
                    {r.title}
                  </span>
                  <span className="block text-[13px] text-[#86868B] mt-0.5">
                    {r.desc}
                  </span>
                </div>

                {/* Chevron */}
                <ChevronRight className="text-[#D1D5DB] transition-all duration-300 group-hover:text-[#1D1D1F] group-hover:translate-x-1" size={20} strokeWidth={2} />
              </button>
            );
          })}
        </div>
        
        {/* Footer */}
        <div className="mt-10 text-center flex items-center justify-center gap-2">
          <div className="w-2 h-2 rounded-full bg-[#34C759] animate-pulse"></div>
          <span className="text-[13px] text-[#86868B] font-medium tracking-wide uppercase">
            System Online • Vercel Edge
          </span>
        </div>
      </div>
    </div>
  );
}
