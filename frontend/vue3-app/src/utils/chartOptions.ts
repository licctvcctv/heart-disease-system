import type { EChartsOption } from 'echarts';
import type {
  AgeAnalysisItem,
  ClinicalFeatureItem,
  FeatureImportanceItem,
  LifestyleAnalysisItem,
  ModelMetricItem,
} from '@/types/dashboard';
import { formatPercent } from './format';

const gridText = '#b4c9d6';
const axisLine = 'rgba(143, 167, 184, 0.22)';
const teal = '#32dbc5';
const cyan = '#51a8ff';
const red = '#ef6363';
const amber = '#f0b35a';
const green = '#71d37f';
const muted = '#6c8091';

const baseTooltip = {
  trigger: 'axis',
  backgroundColor: 'rgba(7, 15, 24, 0.96)',
  borderColor: 'rgba(70, 110, 135, 0.5)',
  textStyle: {
    color: '#e6f0f4',
  },
};

export const createOverviewOption = (prevalenceRate: number): EChartsOption => ({
  tooltip: {
    trigger: 'item',
    backgroundColor: 'rgba(7, 15, 24, 0.96)',
    borderColor: 'rgba(70, 110, 135, 0.5)',
    textStyle: { color: '#e6f0f4' },
    formatter: ({ name, value }: { name: string; value: number }) => {
      const display = name === '患病率' ? formatPercent(value / 100, 1) : formatPercent(value / 100, 1);
      return `${name}<br/>${display}`;
    },
  },
  series: [
    {
      type: 'pie',
      radius: ['64%', '82%'],
      center: ['50%', '52%'],
      avoidLabelOverlap: false,
      label: { show: false },
      labelLine: { show: false },
      data: [
        {
          value: prevalenceRate * 100,
          name: '患病率',
          itemStyle: { color: red },
        },
        {
          value: (1 - prevalenceRate) * 100,
          name: '未患病',
          itemStyle: { color: 'rgba(105, 131, 152, 0.18)' },
        },
      ],
    },
  ],
  graphic: [
    {
      type: 'text',
      left: 'center',
      top: '42%',
      style: {
        text: formatPercent(prevalenceRate, 1),
        fill: '#eff8fb',
        fontSize: 30,
        fontWeight: 700,
      },
    },
    {
      type: 'text',
      left: 'center',
      top: '56%',
      style: {
        text: '总体患病率',
        fill: '#8da3b4',
        fontSize: 12,
      },
    },
  ],
} as EChartsOption);

export const createAgeOption = (items: AgeAnalysisItem[]): EChartsOption => ({
  tooltip: {
    ...baseTooltip,
    formatter: (params: any) => {
      const item = items[params.dataIndex];
      return [
        `${item.ageGroup}`,
        `样本数：${item.sampleCount.toLocaleString('zh-CN')}`,
        `阳性数：${item.positiveCount.toLocaleString('zh-CN')}`,
        `患病率：${formatPercent(item.prevalenceRate, 1)}`,
      ].join('<br/>');
    },
  },
  grid: { left: 42, right: 20, top: 18, bottom: 46 },
  xAxis: {
    type: 'category',
    data: items.map((item) => item.ageGroup),
    axisLine: { lineStyle: { color: axisLine } },
    axisLabel: { color: gridText, interval: 2, rotate: 45, fontSize: 10 },
  },
  yAxis: {
    type: 'value',
    axisLabel: { color: gridText, formatter: '{value}%' },
    splitLine: { lineStyle: { color: 'rgba(143, 167, 184, 0.1)' } },
  },
  series: [
    {
      name: '患病率',
      type: 'bar',
      data: items.map((item) => Number((item.prevalenceRate * 100).toFixed(1))),
      barWidth: 18,
      itemStyle: {
        color: (params: any) => {
          const rate = items[params.dataIndex].prevalenceRate;
          if (rate >= 0.15) return red;
          if (rate >= 0.08) return amber;
          return teal;
        },
      },
      label: {
        show: true,
        position: 'top',
        color: '#dff5ff',
        formatter: (params: any) => `${params.value}%`,
      },
    },
  ],
} as EChartsOption);

export const createLifestyleOption = (items: LifestyleAnalysisItem[]): EChartsOption => ({
  tooltip: {
    ...baseTooltip,
    formatter: (params: any) => {
      const item = items[params.dataIndex];
      return [
        `${item.factor} / ${item.category}`,
        `样本数：${item.sampleCount.toLocaleString('zh-CN')}`,
        `阳性数：${item.positiveCount.toLocaleString('zh-CN')}`,
        `患病率：${formatPercent(item.prevalenceRate, 1)}`,
      ].join('<br/>');
    },
  },
  grid: { left: 112, right: 22, top: 18, bottom: 16 },
  xAxis: {
    type: 'value',
    axisLabel: { color: gridText, formatter: '{value}%' },
    splitLine: { lineStyle: { color: 'rgba(143, 167, 184, 0.1)' } },
  },
  yAxis: {
    type: 'category',
    data: items.map((item) => `${item.factor} · ${item.category}`),
    axisLabel: { color: gridText, width: 100, overflow: 'truncate' },
    axisLine: { lineStyle: { color: axisLine } },
  },
  series: [
    {
      name: '患病率',
      type: 'bar',
      data: items.map((item) => Number((item.prevalenceRate * 100).toFixed(1))),
      barWidth: 14,
      itemStyle: {
        color: (params: any) => {
          const rate = items[params.dataIndex].prevalenceRate;
          return rate >= 0.12 ? red : rate >= 0.08 ? amber : green;
        },
      },
      label: {
        show: true,
        position: 'right',
        color: '#d8edf4',
        formatter: (params: any) => `${params.value}%`,
      },
    },
  ],
} as EChartsOption);

export const createClinicalOption = (feature: ClinicalFeatureItem | undefined) => {
  const groups = feature?.groups || [];

  return {
    tooltip: {
      ...baseTooltip,
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        const item = groups[params.dataIndex];
        if (!item) return '';
        return [
          `${feature?.label || '临床指标'}`,
          `类别：${item.category}`,
          `样本数：${item.sampleCount.toLocaleString('zh-CN')}`,
          `阳性数：${item.positiveCount.toLocaleString('zh-CN')}`,
          `患病率：${formatPercent(item.prevalenceRate, 1)}`,
        ].join('<br/>');
      },
    },
    grid: { left: 124, right: 22, top: 14, bottom: 20 },
    xAxis: {
      type: 'value',
      axisLabel: { color: gridText, formatter: '{value}%' },
      splitLine: { lineStyle: { color: 'rgba(143, 167, 184, 0.1)' } },
    },
    yAxis: {
      type: 'category',
      data: groups.map((item) => item.category),
      axisLabel: { color: gridText, width: 112, overflow: 'truncate' },
      axisLine: { lineStyle: { color: axisLine } },
    },
    series: [
      {
        type: 'bar',
        data: groups.map((item) => Number((item.prevalenceRate * 100).toFixed(1))),
        barWidth: 15,
        itemStyle: {
          color: (params: any) => {
            const rate = groups[params.dataIndex].prevalenceRate;
            if (rate >= 0.35) return red;
            if (rate >= 0.2) return amber;
            return teal;
          },
        },
        label: {
          show: true,
          position: 'right',
          color: '#e2f4fb',
          formatter: (params: any) => `${params.value}%`,
        },
      },
    ],
  } as EChartsOption;
};

export const createModelMetricsOption = (models: ModelMetricItem[]): EChartsOption => ({
  tooltip: {
    ...baseTooltip,
    trigger: 'axis',
    axisPointer: { type: 'shadow' },
  },
  legend: {
    top: 0,
    textStyle: { color: gridText },
  },
  grid: { left: 40, right: 18, top: 42, bottom: 30 },
  xAxis: {
    type: 'category',
    data: models.map((item) => item.name),
    axisLabel: { color: gridText, interval: 0, rotate: 12 },
    axisLine: { lineStyle: { color: axisLine } },
  },
  yAxis: {
    type: 'value',
    max: 1,
    axisLabel: { color: gridText, formatter: '{value}' },
    splitLine: { lineStyle: { color: 'rgba(143, 167, 184, 0.1)' } },
  },
  series: [
    {
      name: 'Accuracy',
      type: 'bar',
      data: models.map((item) => item.accuracy),
      itemStyle: { color: teal },
      barWidth: 12,
    },
    {
      name: 'Precision',
      type: 'bar',
      data: models.map((item) => item.precision),
      itemStyle: { color: cyan },
      barWidth: 12,
    },
    {
      name: 'Recall',
      type: 'bar',
      data: models.map((item) => item.recall),
      itemStyle: { color: amber },
      barWidth: 12,
    },
    {
      name: 'F1',
      type: 'bar',
      data: models.map((item) => item.f1),
      itemStyle: { color: green },
      barWidth: 12,
    },
    {
      name: 'AUC',
      type: 'bar',
      data: models.map((item) => item.auc),
      itemStyle: { color: red },
      barWidth: 12,
    },
  ],
} as EChartsOption);

export const createImportanceBars = (items: FeatureImportanceItem[]) => {
  const maxImportance = Math.max(...items.map((item) => item.importance), 1);

  return items.map((item, index) => {
    const normalized = item.importance / maxImportance;

    return {
    label: item.label,
    value: `${(normalized * 100).toFixed(0)}%`,
    width: `${Math.max(8, normalized * 100)}%`,
    tone: index % 3 === 0 ? 'high' : index % 3 === 1 ? 'medium' : 'low',
    };
  });
};
