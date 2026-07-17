import "server-only";

import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import { getSupabaseUrl, hasSupabaseAdminConfig } from "./config";

let adminClient: SupabaseClient | null = null;

export function getSupabaseAdminClient() {
  if (!hasSupabaseAdminConfig()) {
    throw new Error("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required");
  }

  if (!adminClient) {
    adminClient = createClient(
      getSupabaseUrl() as string,
      process.env.SUPABASE_SERVICE_ROLE_KEY as string,
      {
        auth: {
          autoRefreshToken: false,
          persistSession: false
        }
      }
    );
  }

  return adminClient;
}
