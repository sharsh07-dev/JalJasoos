"use client";
import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useRouter, usePathname } from "next/navigation";

interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (token: string, role: string) => void;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  token: null,
  login: () => {},
  logout: () => {},
  loading: true,
});

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    // Check local storage for user on mount
    const storedUser = localStorage.getItem("jaljasoos_user");
    if (storedUser) {
      setUser(JSON.parse(storedUser));
      setToken("mock-token-vercel");
    } else {
      if (pathname !== "/login") {
        router.push("/login");
      }
    }
    setLoading(false);
  }, [pathname, router]);

  const login = (role: string) => {
    const mockToken = "mock-token-vercel";
    const mockUser = {
      id: "user-" + role.toLowerCase(),
      email: `${role.toLowerCase()}@jaljasoos.com`,
      full_name: role.replace("_", " "),
      role: role
    };
    
    localStorage.setItem("jaljasoos_token", mockToken);
    localStorage.setItem("jaljasoos_user", JSON.stringify(mockUser));
    
    setToken(mockToken);
    setUser(mockUser);
    router.push("/");
  };

  const logout = () => {
    localStorage.removeItem("jaljasoos_token");
    localStorage.removeItem("jaljasoos_user");
    setToken(null);
    setUser(null);
    router.push("/login");
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
