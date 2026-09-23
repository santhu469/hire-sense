"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";

import * as api from "@/lib/api";
import { clearTokens, getStoredTokens, storeTokens } from "@/lib/auth-storage";
import type { User } from "@/lib/types";

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Routed through an async IIFE + .finally() (rather than an early
    // `setIsLoading(false)` in the effect body) so every branch -- including
    // "no stored tokens" -- resolves the loading state from a callback, not
    // synchronously during the effect, avoiding a cascading render.
    (async () => {
      const tokens = getStoredTokens();
      if (!tokens) return;
      try {
        setUser(await api.me());
      } catch {
        clearTokens();
      }
    })().finally(() => setIsLoading(false));
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const tokens = await api.login(email, password);
    storeTokens(tokens.access_token, tokens.refresh_token);
    setUser(await api.me());
  }, []);

  const register = useCallback(async (email: string, password: string) => {
    const tokens = await api.register(email, password);
    storeTokens(tokens.access_token, tokens.refresh_token);
    setUser(await api.me());
  }, []);

  const logout = useCallback(() => {
    clearTokens();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
