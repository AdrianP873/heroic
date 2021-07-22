{{/* Generate application labels */}}
{{- define "application.labels" }}
labels:
  app: {{ .Release.Name }}
{{- end }}