import "server-only";

import { getSupabaseAdminClient } from "./admin";
import { hasSupabaseAdminConfig } from "./config";

type JsonObject = Record<string, unknown>;

type ChartCacheRow = {
  raw_json: JsonObject;
  patterns_json: JsonObject | null;
};

export async function readChartCache({
  userId,
  inputHash
}: {
  userId?: string;
  inputHash: string;
}) {
  if (!userId || !hasSupabaseAdminConfig()) {
    return null;
  }

  const { data, error } = await getSupabaseAdminClient()
    .from("chart_data")
    .select("raw_json, patterns_json")
    .eq("user_id", userId)
    .eq("input_hash", inputHash)
    .maybeSingle<ChartCacheRow>();

  if (error) {
    throw error;
  }

  return data;
}

export async function upsertChartCache({
  userId,
  inputHash,
  rawJson,
  patternsJson
}: {
  userId?: string;
  inputHash: string;
  rawJson: JsonObject;
  patternsJson?: JsonObject | null;
}) {
  if (!userId || !hasSupabaseAdminConfig()) {
    return "disabled" as const;
  }

  const { error } = await getSupabaseAdminClient()
    .from("chart_data")
    .upsert(
      {
        user_id: userId,
        input_hash: inputHash,
        raw_json: rawJson,
        patterns_json: patternsJson ?? null
      },
      {
        onConflict: "user_id,input_hash"
      }
    );

  if (error) {
    throw error;
  }

  return "stored" as const;
}
