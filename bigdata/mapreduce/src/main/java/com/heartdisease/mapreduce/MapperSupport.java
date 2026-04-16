package com.heartdisease.mapreduce;

import java.util.ArrayList;
import java.util.List;

final class MapperSupport {
    static final String NULL_VALUE = "\\N";

    private MapperSupport() {
    }

    static boolean isBlank(String value) {
        return value == null || value.trim().isEmpty() || "?".equals(value.trim());
    }

    static String value(List<String> values, int index) {
        if (index < 0 || index >= values.size()) {
            return NULL_VALUE;
        }
        String value = values.get(index);
        return isBlank(value) ? NULL_VALUE : value.trim();
    }

    static String numeric(List<String> values, int index) {
        String value = value(values, index);
        if (NULL_VALUE.equals(value)) {
            return NULL_VALUE;
        }
        try {
            Double.parseDouble(value);
            return value;
        } catch (NumberFormatException ignored) {
            return NULL_VALUE;
        }
    }

    static String intNumeric(List<String> values, int index) {
        String value = numeric(values, index);
        if (NULL_VALUE.equals(value)) {
            return NULL_VALUE;
        }
        try {
            return Integer.toString((int) Math.round(Double.parseDouble(value)));
        } catch (NumberFormatException ignored) {
            return NULL_VALUE;
        }
    }

    static String yesNo(String value) {
        if (isBlank(value)) {
            return NULL_VALUE;
        }
        return "yes".equalsIgnoreCase(value.trim()) ? "1" : "0";
    }

    static String sexCode(String value) {
        if (isBlank(value)) {
            return NULL_VALUE;
        }
        String text = value.trim().toLowerCase();
        if ("male".equals(text) || "1".equals(text) || "1.0".equals(text)) {
            return "1";
        }
        if ("female".equals(text) || "0".equals(text) || "0.0".equals(text)) {
            return "0";
        }
        return NULL_VALUE;
    }

    static String diabetesFlag(String value) {
        if (isBlank(value)) {
            return NULL_VALUE;
        }
        String text = value.trim().toLowerCase();
        if (text.startsWith("yes") || text.contains("borderline") || text.contains("prediabetes")) {
            return "1";
        }
        return "0";
    }

    static String smokerStatusFlag(String value) {
        if (isBlank(value)) {
            return NULL_VALUE;
        }
        String text = value.trim().toLowerCase();
        if (text.contains("never")) {
            return "0";
        }
        if (text.contains("former") || text.contains("current") || text.contains("smoker")) {
            return "1";
        }
        return NULL_VALUE;
    }

    static String ageBandFromNumber(String value) {
        if (isBlank(value)) {
            return NULL_VALUE;
        }
        try {
            int age = (int) Math.round(Double.parseDouble(value.trim()));
            if (age < 35) return "18-34";
            if (age < 45) return "35-44";
            if (age < 55) return "45-54";
            if (age < 65) return "55-64";
            return "65+";
        } catch (NumberFormatException ignored) {
            return NULL_VALUE;
        }
    }

    static String riskFromDiagnosis(String value) {
        if (isBlank(value)) {
            return NULL_VALUE;
        }
        try {
            return Double.parseDouble(value.trim()) > 0 ? "1" : "0";
        } catch (NumberFormatException ignored) {
            return NULL_VALUE;
        }
    }

    static String tsv(String... values) {
        List<String> normalized = new ArrayList<>(values.length);
        for (String value : values) {
            normalized.add(isBlank(value) ? NULL_VALUE : value.trim());
        }
        return String.join("\t", normalized);
    }
}
