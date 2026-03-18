import { motion } from 'framer-motion';
import { BUILT_IN_TEMPLATES, BuiltInTemplateId } from '../../types/template';

interface Props {
  selected: BuiltInTemplateId;
  onChange: (id: BuiltInTemplateId) => void;
}

const badgeColor: Record<string, string> = {
  Recommended: 'bg-purple-100 text-purple-700',
  Fast:        'bg-blue-100 text-blue-700',
  Testers:     'bg-green-100 text-green-700',
  'CI/CD':     'bg-orange-100 text-orange-700',
};

export function TemplateSelector({ selected, onChange }: Props) {
  return (
    <div className="grid grid-cols-2 gap-4">
      {BUILT_IN_TEMPLATES.map((tpl, i) => {
        const isSelected = selected === tpl.id;
        const tableFields = tpl.fields.filter(f => f.showInTable).map(f => f.label);
        const expandFields = tpl.fields.filter(f => f.showInExpand).map(f => f.label);
        return (
          <motion.button
            key={tpl.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            onClick={() => onChange(tpl.id)}
            className={`text-left p-5 rounded-2xl border-2 transition-all ${
              isSelected
                ? 'border-purple-400 bg-purple-50 shadow-sm'
                : 'border-gray-200 bg-white hover:border-purple-200 hover:bg-gray-50'
            }`}
          >
            <div className="flex items-start justify-between mb-2">
              <span className="text-2xl">{tpl.icon}</span>
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${badgeColor[tpl.badge] ?? 'bg-gray-100 text-gray-600'}`}>
                {tpl.badge}
              </span>
            </div>
            <p className={`font-semibold text-sm mb-1 ${isSelected ? 'text-purple-800' : 'text-gray-800'}`}>
              {tpl.name}
            </p>
            <p className="text-xs text-gray-500 mb-3 leading-relaxed">{tpl.description}</p>

            <div className="space-y-1.5">
              {tableFields.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-1">Table columns</p>
                  <div className="flex flex-wrap gap-1">
                    {tableFields.map(f => (
                      <span key={f} className={`text-xs px-1.5 py-0.5 rounded font-mono ${
                        isSelected ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-600'
                      }`}>
                        {f}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              {expandFields.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-1">Expanded detail</p>
                  <div className="flex flex-wrap gap-1">
                    {expandFields.map(f => (
                      <span key={f} className={`text-xs px-1.5 py-0.5 rounded font-mono ${
                        isSelected ? 'bg-purple-50 text-purple-500' : 'bg-gray-50 text-gray-400'
                      }`}>
                        {f}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {isSelected && (
              <div className="mt-3 flex items-center gap-1.5 text-purple-600 text-xs font-medium">
                <span className="w-4 h-4 rounded-full bg-purple-500 text-white flex items-center justify-center text-[10px]">✓</span>
                Selected
              </div>
            )}
          </motion.button>
        );
      })}
    </div>
  );
}
